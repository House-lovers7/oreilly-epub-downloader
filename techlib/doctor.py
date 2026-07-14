"""Diagnostic contract (implemented through TDD)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
    return DoctorReport(ok=True, findings=[], metrics={})
