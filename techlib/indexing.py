"""Incremental indexing contract (implemented through TDD)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IngestResult:
    doc_id: str
    title: str
    section_count: int
    chunk_count: int
    changed: bool
    manifest_path: Path


class IncrementalIndexer:
    def __init__(self, kb_dir: Path, *, chunk_chars: int = 5000):
        self.kb_dir = Path(kb_dir)
        self.chunk_chars = chunk_chars

    def ingest(self, source: Path, *, rights: str) -> IngestResult:
        return IngestResult("", "", 0, 0, False, self.kb_dir / "manifest.json")
