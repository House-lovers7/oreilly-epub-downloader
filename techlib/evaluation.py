"""Skill utility scoring contract (implemented through TDD)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UtilityEvaluation:
    passed: bool
    metrics: dict[str, float | int]
    failures: list[str]


def evaluate_pairs(
    cases: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
    assisted: list[dict[str, Any]],
) -> UtilityEvaluation:
    return UtilityEvaluation(passed=True, metrics={}, failures=[])
