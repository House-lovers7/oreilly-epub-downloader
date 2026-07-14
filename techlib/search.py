"""Progressive, offline-first retrieval for the local knowledge library."""
from __future__ import annotations

import json
import math
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


CARD_FILES = ("practices.jsonl", "antipatterns.jsonl", "tradeoffs.jsonl")
WORD_RE = re.compile(r"[\w\u3040-\u30ff\u3400-\u9fff]+", re.UNICODE)


@dataclass(frozen=True)
class RetrievalResult:
    stage: str
    query: str
    items: list[dict[str, Any]] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)
    network_used: bool = False
    reason: str = ""


class SearchEngine:
    """Retrieve the smallest sufficient evidence layer.

    The engine never performs network access.  It first checks active distilled
    cards, then opens the SQLite FTS index read-only.  Full section text is only
    available through :meth:`get_section`.
    """

    def __init__(
        self,
        kb_dir: Path,
        *,
        excerpt_chars: int = 700,
        vector_search: Callable[[str, int], list[dict[str, Any]]] | None = None,
    ):
        self.kb_dir = Path(kb_dir)
        self.excerpt_chars = excerpt_chars
        self.vector_search = vector_search

    def search(
        self,
        query: str,
        *,
        domain: str | None = None,
        limit: int = 5,
        source_type: str | None = None,
    ) -> RetrievalResult:
        query = query.strip()
        if not query:
            raise ValueError("query must not be empty")
        if limit < 1 or limit > 50:
            raise ValueError("limit must be between 1 and 50")

        cards = (
            self.search_cards(query, domain=domain, limit=limit)
            if source_type is None
            else []
        )
        if cards:
            return RetrievalResult(
                stage="cards",
                query=query,
                items=cards,
                trace=["cards"],
                reason="active_card_match",
            )

        chunks = self.search_chunks(query, limit=limit, source_type=source_type)
        if chunks:
            return RetrievalResult(
                stage="fts",
                query=query,
                items=chunks,
                trace=["cards", "fts"],
                reason="card_evidence_insufficient",
            )

        if self.vector_search is not None:
            vector_items = self.vector_search(query, limit)
            if vector_items:
                return RetrievalResult(
                    stage="vector",
                    query=query,
                    items=vector_items,
                    trace=["cards", "fts", "vector"],
                    reason="lexical_evidence_insufficient",
                )
            return RetrievalResult(
                stage="insufficient_evidence",
                query=query,
                trace=["cards", "fts", "vector"],
                reason="no_local_evidence",
            )

        return RetrievalResult(
            stage="insufficient_evidence",
            query=query,
            trace=["cards", "fts"],
            reason="no_local_evidence",
        )

    def search_cards(
        self, query: str, *, domain: str | None = None, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Search only active cards; candidate cards never leak into results."""
        return self._search_cards(query, domain=domain, limit=limit)

    def list_cards(
        self,
        *,
        domain: str | None = None,
        card_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return card metadata with its effective lifecycle state."""
        root = self.kb_dir / "cards"
        if domain:
            directories = [root / _plain_domain(domain)]
        elif root.exists():
            directories = sorted(path for path in root.iterdir() if path.is_dir())
        else:
            directories = []
        lifecycle = self._load_lifecycle()
        cards: list[dict[str, Any]] = []
        for directory in directories:
            for filename in CARD_FILES:
                path = directory / filename
                if not path.exists():
                    continue
                for line in path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    card = json.loads(line)
                    effective_status = self._card_status(card, lifecycle)
                    if card_type and card.get("type") != card_type:
                        continue
                    if status and effective_status != status:
                        continue
                    item = dict(card)
                    item["status"] = effective_status
                    cards.append(item)
        return cards

    def search_chunks(
        self, query: str, *, limit: int = 5, source_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Search bounded FTS excerpts without loading full documents."""
        return self._search_fts(query, limit=limit, source_type=source_type)

    def get_section(self, chunk_id: str) -> dict[str, Any] | None:
        db = self._db_path()
        if not db.exists():
            return None
        with self._connect_read_only() as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """
                SELECT chunk_id, doc_id, title, heading, source_ref,
                       source_path, source_type, text
                FROM chunks WHERE chunk_id = ?
                """,
                (chunk_id,),
            ).fetchone()
        return dict(row) if row else None

    def _search_cards(
        self, query: str, *, domain: str | None, limit: int
    ) -> list[dict[str, Any]]:
        terms = _query_terms(query)
        if not terms:
            return []
        scored: list[tuple[float, str, dict[str, Any]]] = []
        for card in self.list_cards(domain=domain, status="active"):
            score = _card_score(card, terms)
            if score <= 0:
                continue
            item = dict(card)
            item["match_score"] = round(score, 4)
            scored.append((score, str(card.get("card_id", "")), item))
        scored.sort(key=lambda entry: (-entry[0], entry[1]))
        return [item for _, _, item in scored[:limit]]

    def _load_lifecycle(self) -> dict[str, Any]:
        path = self.kb_dir / "cards" / "lifecycle.json"
        if not path.exists():
            return {"default_status": "candidate", "overrides": {}}
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("cards/lifecycle.json must contain an object")
        return data

    @staticmethod
    def _card_status(card: dict[str, Any], lifecycle: dict[str, Any]) -> str:
        card_id = str(card.get("card_id", ""))
        overrides = lifecycle.get("overrides", {})
        override = overrides.get(card_id) if isinstance(overrides, dict) else None
        if isinstance(override, str):
            return override
        if isinstance(override, dict) and isinstance(override.get("status"), str):
            return override["status"]
        return str(card.get("status") or lifecycle.get("default_status") or "candidate")

    def _search_fts(
        self, query: str, *, limit: int, source_type: str | None = None
    ) -> list[dict[str, Any]]:
        db = self._db_path()
        if not db.exists():
            return []
        fts_query = _safe_fts_query(query)
        if not fts_query:
            return []
        if source_type is not None and source_type not in {
            "epub",
            "pdf",
            "md",
            "markdown",
            "txt",
        }:
            raise ValueError("unsupported source_type filter")
        source_clause = " AND c.source_type = ?" if source_type else ""
        terms = list(dict.fromkeys(_query_terms(query)))
        try:
            with self._connect_read_only() as connection:
                connection.row_factory = sqlite3.Row
                rows = _execute_fts(
                    connection,
                    fts_query,
                    source_clause=source_clause,
                    source_type=source_type,
                    limit=limit,
                )
                retrieval_mode = "strict_and"
                if not rows and len(terms) >= 3:
                    candidate_limit = min(500, max(100, limit * 30))
                    relaxed = _execute_fts(
                        connection,
                        _safe_fts_query(query, operator="OR"),
                        source_clause=source_clause,
                        source_type=source_type,
                        limit=candidate_limit,
                    )
                    minimum_matches = max(2, math.ceil(len(terms) * 0.4))
                    candidates: list[tuple[int, float, str, sqlite3.Row]] = []
                    for row in relaxed:
                        haystack = " ".join(
                            str(row[field])
                            for field in ("title", "heading", "text")
                        ).casefold()
                        matches = sum(term in haystack for term in terms)
                        if matches >= minimum_matches:
                            candidates.append(
                                (
                                    matches,
                                    float(row["score"]),
                                    str(row["chunk_id"]),
                                    row,
                                )
                            )
                    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
                    rows = [row for _, _, _, row in candidates[:limit]]
                    retrieval_mode = "relaxed_or"
        except sqlite3.OperationalError:
            return []

        results: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            text = _normalize_text(str(item.pop("text", "")))
            item["retrieval_mode"] = retrieval_mode
            item["excerpt"] = text[: self.excerpt_chars] + (
                "…" if len(text) > self.excerpt_chars else ""
            )
            results.append(item)
        return results

    def _db_path(self) -> Path:
        return self.kb_dir / "index" / "library.sqlite"

    def _connect_read_only(self) -> sqlite3.Connection:
        return sqlite3.connect(f"file:{self._db_path()}?mode=ro", uri=True)


def _plain_domain(domain: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", domain):
        raise ValueError("domain must be a lowercase plain name")
    return domain


def _query_terms(query: str) -> list[str]:
    return [term.casefold() for term in WORD_RE.findall(query) if len(term) >= 2]


def _card_score(card: dict[str, Any], terms: list[str]) -> float:
    fields = {
        "title": card.get("title"),
        "problem": card.get("problem"),
        "recommendation": card.get("recommendation"),
        "pitfalls": card.get("pitfalls"),
        "when_not_to_apply": card.get("when_not_to_apply"),
        "keywords": card.get("keywords"),
    }
    searchable = json.dumps(fields, ensure_ascii=False).casefold()
    matches = sum(1 for term in terms if term in searchable)
    return matches / len(terms) if terms else 0.0


def _safe_fts_query(query: str, *, operator: str = "AND") -> str:
    terms = _query_terms(query)
    if operator not in {"AND", "OR"}:
        raise ValueError("unsupported FTS operator")
    return f" {operator} ".join(
        f'"{term.replace(chr(34), chr(34) * 2)}"*' for term in terms
    )


def _execute_fts(
    connection: sqlite3.Connection,
    query: str,
    *,
    source_clause: str,
    source_type: str | None,
    limit: int,
) -> list[sqlite3.Row]:
    parameters: tuple[Any, ...] = (
        (query, source_type, limit) if source_type else (query, limit)
    )
    return connection.execute(
        f"""
        SELECT c.chunk_id, c.doc_id, c.title, c.heading,
               c.source_ref, c.source_path, c.source_type, c.text,
               bm25(chunks_fts) AS score
        FROM chunks_fts
        JOIN chunks c ON c.chunk_id = chunks_fts.chunk_id
        WHERE chunks_fts MATCH ?{source_clause}
        ORDER BY score
        LIMIT ?
        """,
        parameters,
    ).fetchall()


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
