"""Deterministic paired scoring for knowledge-supply skill utility."""
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
    failures: list[str] = []
    case_map = _unique_by_task_id(cases)
    baseline_map = _unique_by_task_id(baseline)
    assisted_map = _unique_by_task_id(assisted)
    expected_ids = set(case_map)

    if (
        len(cases) < 12
        or len(case_map) != len(cases)
        or set(baseline_map) != expected_ids
        or set(assisted_map) != expected_ids
        or len(baseline_map) != len(baseline)
        or len(assisted_map) != len(assisted)
    ):
        failures.append("case_alignment")

    negative_ids = {
        task_id
        for task_id, case in case_map.items()
        if case.get("should_use_library") is False
    }
    if len(negative_ids) < 4:
        failures.append("negative_case_coverage")

    paired_ids = sorted(expected_ids & set(baseline_map) & set(assisted_map))
    baseline_accepted = sum(
        _nonnegative_int(baseline_map[task_id].get("accepted_findings"))
        for task_id in paired_ids
    )
    assisted_accepted = sum(
        _nonnegative_int(assisted_map[task_id].get("accepted_findings"))
        for task_id in paired_ids
    )
    false_positives = sum(
        _nonnegative_int(assisted_map[task_id].get("false_positives"))
        for task_id in paired_ids
    )
    finding_total = assisted_accepted + false_positives
    false_positive_rate = false_positives / finding_total if finding_total else 0.0

    citations_total = sum(
        _nonnegative_int(assisted_map[task_id].get("citations_total"))
        for task_id in paired_ids
    )
    citations_valid = sum(
        _nonnegative_int(assisted_map[task_id].get("citations_valid"))
        for task_id in paired_ids
    )
    citation_accuracy = citations_valid / citations_total if citations_total else 0.0

    baseline_duration = sum(
        _nonnegative_float(baseline_map[task_id].get("duration_ms"))
        for task_id in paired_ids
    )
    assisted_duration = sum(
        _nonnegative_float(assisted_map[task_id].get("duration_ms"))
        for task_id in paired_ids
    )
    baseline_context = sum(
        _nonnegative_float(baseline_map[task_id].get("context_tokens"))
        for task_id in paired_ids
    )
    assisted_context = sum(
        _nonnegative_float(assisted_map[task_id].get("context_tokens"))
        for task_id in paired_ids
    )
    duration_overhead = _overhead_ratio(baseline_duration, assisted_duration)
    context_overhead = _overhead_ratio(baseline_context, assisted_context)
    leakage_events = sum(
        _nonnegative_int(assisted_map[task_id].get("leakage_events"))
        for task_id in paired_ids
    )
    negative_case_violations = sum(
        1
        for task_id in negative_ids & set(assisted_map)
        if assisted_map[task_id].get("library_used") is True
    )

    metrics: dict[str, float | int] = {
        "case_count": len(case_map),
        "negative_case_count": len(negative_ids),
        "accepted_finding_gain": assisted_accepted - baseline_accepted,
        "false_positive_rate": false_positive_rate,
        "citation_accuracy": citation_accuracy,
        "duration_overhead": duration_overhead,
        "context_overhead": context_overhead,
        "leakage_events": leakage_events,
        "negative_case_violations": negative_case_violations,
    }

    if metrics["accepted_finding_gain"] <= 0:
        failures.append("accepted_finding_gain")
    if false_positive_rate > 0.10:
        failures.append("false_positive_rate")
    if citation_accuracy != 1.0:
        failures.append("citation_accuracy")
    if duration_overhead > 0.30:
        failures.append("duration_overhead")
    if context_overhead > 0.30:
        failures.append("context_overhead")
    if leakage_events:
        failures.append("leakage")
    if negative_case_violations:
        failures.append("negative_case_violations")

    failures = list(dict.fromkeys(failures))
    return UtilityEvaluation(passed=not failures, metrics=metrics, failures=failures)


def _unique_by_task_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        task_id = row.get("task_id")
        if isinstance(task_id, str) and task_id:
            result[task_id] = row
    return result


def _nonnegative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _nonnegative_float(value: Any) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


def _overhead_ratio(baseline: float, assisted: float) -> float:
    if baseline == 0:
        return float("inf") if assisted else 0.0
    return max(0.0, (assisted - baseline) / baseline)
