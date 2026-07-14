"""Lazy vector retrieval contract (implemented through TDD)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


class LazyVectorSearch:
    def __init__(
        self,
        kb_dir: Path,
        *,
        embed_query: Callable[[str, str], list[float]] | None = None,
        max_working_bytes: int = 256 * 1024 * 1024,
    ):
        self.kb_dir = Path(kb_dir)
        self.embed_query = embed_query
        self.max_working_bytes = max_working_bytes

    def __call__(self, query: str, limit: int) -> list[dict[str, Any]]:
        return []
