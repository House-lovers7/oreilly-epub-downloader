"""Read-only integrity diagnostics for the local knowledge supply system."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .cache import CacheManager
from .lifecycle import CardLifecycle, STATUSES


CARD_FILES = ("practices.jsonl", "antipatterns.jsonl", "tradeoffs.jsonl")
REQUIRED_CARD_FIELDS = {
    "card_id",
    "domain",
    "type",
    "title",
    "problem",
    "recommendation",
    "pitfalls",
    "when_not_to_apply",
    "keywords",
    "source_chunks",
    "source_books",
    "confidence",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DoctorReport:
    ok: bool
    findings: list[Finding]
    metrics: dict[str, Any]


def run_doctor(repo: Path, *, soft_limit_bytes: int = 5 * 1024**3) -> DoctorReport:
    """Inspect local assets without mutating, downloading, or loading full books."""

    repo = Path(repo)
    kb = repo / "knowledge-base"
    findings: list[Finding] = []
    metrics: dict[str, Any] = {
        "cards_total": 0,
        "cards_candidate": 0,
        "cards_active": 0,
        "cards_deprecated": 0,
        "cards_archived": 0,
        "documents": 0,
        "chunks": 0,
        "missing_provenance": 0,
    }

    chunk_ids = _inspect_index(kb, findings, metrics)
    _inspect_cards(kb, chunk_ids, findings, metrics)

    cache = CacheManager(repo, soft_limit_bytes=soft_limit_bytes).status()
    metrics.update(
        {
            "cache_total_bytes": cache.total_bytes,
            "cache_hot_bytes": cache.hot_bytes,
            "cache_derived_bytes": cache.derived_bytes,
            "cache_raw_bytes": cache.raw_bytes,
            "cache_soft_limit_bytes": cache.soft_limit_bytes,
            "cache_warning": cache.warning,
        }
    )
    if cache.warning:
        findings.append(
            Finding(
                severity="warning",
                code="cache_soft_limit_warning",
                message="Local assets have reached at least 80% of the soft cache limit.",
                details={
                    "total_bytes": cache.total_bytes,
                    "soft_limit_bytes": cache.soft_limit_bytes,
                },
            )
        )

    return DoctorReport(
        ok=not any(finding.severity == "error" for finding in findings),
        findings=findings,
        metrics=metrics,
    )


def _inspect_index(
    kb: Path, findings: list[Finding], metrics: dict[str, Any]
) -> set[str]:
    db = kb / "index" / "library.sqlite"
    if not db.exists():
        findings.append(
            Finding(
                severity="warning",
                code="index_missing",
                message="The local full-text index does not exist yet.",
            )
        )
        return set()

    try:
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as connection:
            integrity = connection.execute("PRAGMA quick_check").fetchone()
            if not integrity or integrity[0] != "ok":
                findings.append(
                    Finding(
                        severity="error",
                        code="index_integrity",
                        message="SQLite quick_check did not return ok.",
                        details={"result": integrity[0] if integrity else None},
                    )
                )
            metrics["documents"] = int(
                connection.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
            )
            metrics["chunks"] = int(
                connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            )
            return {
                str(row[0])
                for row in connection.execute("SELECT chunk_id FROM chunks")
            }
    except sqlite3.Error as error:
        findings.append(
            Finding(
                severity="error",
                code="index_unreadable",
                message="The SQLite index could not be inspected read-only.",
                details={"error": str(error)},
            )
        )
        return set()


def _inspect_cards(
    kb: Path,
    chunk_ids: set[str],
    findings: list[Finding],
    metrics: dict[str, Any],
) -> None:
    cards_root = kb / "cards"
    lifecycle = CardLifecycle(cards_root / "lifecycle.json")
    seen_ids: set[str] = set()

    for path in _card_paths(cards_root):
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            location = {"path": str(path), "line": line_number}
            try:
                card = json.loads(line)
            except json.JSONDecodeError as error:
                findings.append(
                    Finding(
                        severity="error",
                        code="card_invalid_json",
                        message="A card line is not valid JSON.",
                        details={**location, "error": str(error)},
                    )
                )
                continue
            if not isinstance(card, dict):
                findings.append(
                    Finding(
                        severity="error",
                        code="card_invalid_shape",
                        message="A card line must contain a JSON object.",
                        details=location,
                    )
                )
                continue

            metrics["cards_total"] += 1
            missing = sorted(
                field for field in REQUIRED_CARD_FIELDS if not _present(card.get(field))
            )
            if missing:
                findings.append(
                    Finding(
                        severity="error",
                        code="card_schema",
                        message="A card is missing required fields.",
                        details={**location, "missing_fields": missing},
                    )
                )

            card_id = str(card.get("card_id", ""))
            if card_id in seen_ids:
                findings.append(
                    Finding(
                        severity="error",
                        code="duplicate_card_id",
                        message="A card_id is defined more than once.",
                        details={**location, "card_id": card_id},
                    )
                )
            elif card_id:
                seen_ids.add(card_id)

            try:
                status = lifecycle.status(card_id)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                findings.append(
                    Finding(
                        severity="error",
                        code="lifecycle_invalid",
                        message="The card lifecycle registry is invalid.",
                        details={"error": str(error)},
                    )
                )
                status = "candidate"
            if status not in STATUSES:
                findings.append(
                    Finding(
                        severity="error",
                        code="card_status",
                        message="A card has an unknown lifecycle status.",
                        details={**location, "card_id": card_id, "status": status},
                    )
                )
            else:
                metrics[f"cards_{status}"] += 1

            references = card.get("source_chunks")
            if not isinstance(references, list):
                references = []
            missing_chunks = sorted(
                str(reference)
                for reference in references
                if str(reference) not in chunk_ids
            )
            if missing_chunks:
                metrics["missing_provenance"] += len(missing_chunks)
                findings.append(
                    Finding(
                        severity="error",
                        code="missing_provenance",
                        message="A card references chunks absent from the local index.",
                        details={
                            **location,
                            "card_id": card_id,
                            "missing_chunk_ids": missing_chunks,
                        },
                    )
                )


def _card_paths(cards_root: Path) -> list[Path]:
    if not cards_root.exists():
        return []
    return sorted(
        path
        for directory in cards_root.iterdir()
        if directory.is_dir()
        for name in CARD_FILES
        if (path := directory / name).is_file()
    )


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True
