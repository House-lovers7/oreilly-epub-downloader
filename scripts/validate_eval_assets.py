#!/usr/bin/env python3
"""Validate the dependency-free structural contract of utility eval assets."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cases = json.loads(
        (ROOT / "evals" / "skill-utility-cases.json").read_text(encoding="utf-8")
    )
    failures: list[str] = []
    if not isinstance(cases, list) or len(cases) < 12:
        failures.append("case_count")
        cases = cases if isinstance(cases, list) else []
    ids = [case.get("task_id") for case in cases if isinstance(case, dict)]
    if len(set(ids)) != len(cases) or any(not value for value in ids):
        failures.append("unique_task_ids")
    negative_count = sum(
        case.get("should_use_library") is False
        for case in cases
        if isinstance(case, dict)
    )
    if negative_count < 4:
        failures.append("negative_case_coverage")
    payload = {
        "ok": not failures,
        "case_count": len(cases),
        "negative_case_count": negative_count,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
