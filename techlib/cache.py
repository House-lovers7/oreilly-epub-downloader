"""Public cache-management contract (implemented through TDD)."""
from __future__ import annotations

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
        return CacheStatus(0, 0, 0, 0, self.soft_limit_bytes, False)

    def prune_plan(self, *, target_bytes: int) -> list[Path]:
        return []
