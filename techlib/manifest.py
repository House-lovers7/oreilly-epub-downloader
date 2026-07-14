"""Content-addressed provenance manifests for incrementally derived assets."""
from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
from typing import Any


def build_source_manifest(path: Path, *, rights: str, extractor_version: str) -> dict[str, Any]:
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"source is not a regular file: {path}")
    digest = file_sha256(path)
    return {
        "source_path": str(path),
        "source_id": digest[:16],
        "source_size": path.stat().st_size,
        "rights": rights,
        "extractor_version": extractor_version,
        "source_sha256": digest,
        "captured_at": dt.datetime.now(dt.UTC).isoformat(),
    }


def manifest_is_stale(manifest: dict[str, Any], path: Path) -> bool:
    path = Path(path)
    if not path.is_file():
        return True
    expected_size = manifest.get("source_size")
    if isinstance(expected_size, int) and path.stat().st_size != expected_size:
        return True
    expected_hash = manifest.get("source_sha256")
    return not isinstance(expected_hash, str) or file_sha256(path) != expected_hash


def file_sha256(path: Path, *, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(block_size):
            digest.update(block)
    return digest.hexdigest()
