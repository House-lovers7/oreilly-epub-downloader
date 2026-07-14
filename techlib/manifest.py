"""Public provenance-manifest contract (implemented through TDD)."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def build_source_manifest(path: Path, *, rights: str, extractor_version: str) -> dict[str, Any]:
    return {
        "source_path": str(path),
        "rights": rights,
        "extractor_version": extractor_version,
        "source_sha256": "",
    }


def manifest_is_stale(manifest: dict[str, Any], path: Path) -> bool:
    return False
