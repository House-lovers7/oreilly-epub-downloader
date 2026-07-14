"""Budget reporting and non-destructive pruning plans for local assets."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CacheStatus:
    total_bytes: int
    hot_bytes: int
    derived_bytes: int
    raw_bytes: int
    soft_limit_bytes: int
    warning: bool


class CacheManager:
    def __init__(self, repo: Path, *, soft_limit_bytes: int):
        self.repo = Path(repo)
        self.soft_limit_bytes = soft_limit_bytes

    def status(self) -> CacheStatus:
        raw_bytes = _tree_size(self.repo / "downloads")
        hot_bytes = sum(
            _tree_size(path)
            for path in (
                self.repo / "knowledge-base" / "catalog.json",
                self.repo / "knowledge-base" / "cards",
                self.repo / "knowledge-base" / "index" / "library.sqlite",
                self.repo / "knowledge-base" / "index" / "library.sqlite-wal",
                self.repo / "knowledge-base" / "index" / "library.sqlite-shm",
            )
        )
        derived_bytes = sum(_file_size(path) for path in self._derived_files())
        total_bytes = raw_bytes + hot_bytes + derived_bytes
        return CacheStatus(
            total_bytes=total_bytes,
            hot_bytes=hot_bytes,
            derived_bytes=derived_bytes,
            raw_bytes=raw_bytes,
            soft_limit_bytes=self.soft_limit_bytes,
            warning=total_bytes >= int(self.soft_limit_bytes * 0.8),
        )

    def prune_plan(self, *, target_bytes: int) -> list[Path]:
        if target_bytes <= 0:
            return []
        candidates = sorted(
            self._derived_files(), key=lambda path: (path.stat().st_atime, str(path))
        )
        selected: list[Path] = []
        reclaimed = 0
        for path in candidates:
            selected.append(path)
            reclaimed += _file_size(path)
            if reclaimed >= target_bytes:
                break
        return selected

    def _derived_files(self) -> list[Path]:
        files: list[Path] = []
        books = self.repo / "knowledge-base" / "books"
        if books.exists():
            files.extend(path for path in books.rglob("*") if path.is_file())
        index = self.repo / "knowledge-base" / "index"
        if index.exists():
            files.extend(
                path
                for path in index.glob("embeddings*")
                if path.is_file() and not path.is_symlink()
            )
        return files


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size if path.is_file() and not path.is_symlink() else 0
    except OSError:
        return 0


def _tree_size(path: Path) -> int:
    if path.is_file():
        return _file_size(path)
    if not path.exists():
        return 0
    total = 0
    for root, directories, filenames in os.walk(path, followlinks=False):
        directories[:] = [
            name for name in directories if not (Path(root) / name).is_symlink()
        ]
        total += sum(_file_size(Path(root) / filename) for filename in filenames)
    return total
