"""Public retrieval contract (implemented through TDD)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RetrievalResult:
    stage: str
    query: str
    items: list[dict[str, Any]] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)
    network_used: bool = False
    reason: str = ""


class SearchEngine:
    def __init__(self, kb_dir: Path):
        self.kb_dir = Path(kb_dir)

    def search(self, query: str, *, domain: str | None = None, limit: int = 5) -> RetrievalResult:
        return RetrievalResult(
            stage="insufficient_evidence",
            query=query,
            trace=["cards"],
            reason="not implemented",
        )

    def get_section(self, chunk_id: str) -> dict[str, Any] | None:
        return None
