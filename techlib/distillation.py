"""Explicit, local-only preparation of bounded card distillation material."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .search import SearchEngine


@dataclass(frozen=True)
class DomainPackResult:
    domain: str
    chunk_count: int
    book_count: int
    pack_path: Path
    manifest_path: Path


def build_domain_pack(
    kb_dir: Path,
    domain: str,
    queries: list[str],
    *,
    limit_per_query: int = 40,
    max_chunks: int = 120,
    source_type: str | None = None,
    output_dir: Path | None = None,
) -> DomainPackResult:
    """Create a replace-on-success pack only when explicitly invoked."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", domain):
        raise ValueError("domain must be a lowercase plain name")
    normalized_queries = [query.strip() for query in queries if query.strip()]
    if not normalized_queries:
        raise ValueError("at least one non-empty query is required")
    if limit_per_query < 1 or max_chunks < 1:
        raise ValueError("pack limits must be positive")

    kb_dir = Path(kb_dir)
    engine = SearchEngine(kb_dir)
    best: dict[str, dict[str, Any]] = {}
    for query in normalized_queries:
        for result in engine.search_chunks(
            query, limit=limit_per_query, source_type=source_type
        ):
            chunk_id = str(result["chunk_id"])
            entry = best.get(chunk_id)
            if entry is not None:
                entry["matched_queries"].append(query)
                entry["score"] = min(float(entry["score"]), float(result["score"]))
                continue
            section = engine.get_section(chunk_id)
            if section is None:
                continue
            best[chunk_id] = {
                "chunk_id": chunk_id,
                "doc_id": section["doc_id"],
                "title": section["title"],
                "heading": section["heading"],
                "source_ref": section["source_ref"],
                "source_type": section["source_type"],
                "score": float(result["score"]),
                "matched_queries": [query],
                "text": section["text"],
            }

    rows = sorted(best.values(), key=lambda row: (row["score"], row["chunk_id"]))[
        :max_chunks
    ]
    destination = Path(output_dir) if output_dir else kb_dir / "cards" / domain
    pack_path = destination / "source-pack.jsonl"
    manifest_path = destination / "manifest.json"
    pack_text = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in rows
    )
    _atomic_write_text(pack_path, pack_text)
    manifest = {
        "schema_version": 1,
        "domain": domain,
        "queries": normalized_queries,
        "chunk_count": len(rows),
        "book_count": len({row["doc_id"] for row in rows}),
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "pack_sha256": hashlib.sha256(pack_text.encode("utf-8")).hexdigest(),
        "next_card_status": "candidate",
        "policy": (
            "Local distillation material only. Reconstruct decision criteria, "
            "procedures, and pitfalls; do not reproduce long source passages."
        ),
    }
    _atomic_write_text(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    return DomainPackResult(
        domain=domain,
        chunk_count=len(rows),
        book_count=manifest["book_count"],
        pack_path=pack_path,
        manifest_path=manifest_path,
    )


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
