from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from techlib.doctor import run_doctor
from techlib.evaluation import evaluate_pairs
from tests.kb_fixture import add_card, create_index


def observations(*, assisted: bool, false_positives: int = 0) -> list[dict]:
    rows = []
    for index in range(12):
        should_use = index < 8
        rows.append(
            {
                "task_id": f"task-{index:02d}",
                "library_used": should_use if assisted else False,
                "accepted_findings": 2 if assisted and should_use else 1,
                "false_positives": false_positives if index == 0 else 0,
                "duration_ms": 120 if assisted else 100,
                "context_tokens": 1200 if assisted else 1000,
                "citations_total": 2 if assisted and should_use else 0,
                "citations_valid": 2 if assisted and should_use else 0,
                "leakage_events": 0,
            }
        )
    return rows


CASES = [
    {"task_id": f"task-{index:02d}", "should_use_library": index < 8}
    for index in range(12)
]


class DoctorTests(unittest.TestCase):
    def test_missing_provenance_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            kb = repo / "knowledge-base"
            create_index(kb)
            add_card(kb, status="candidate")

            report = run_doctor(repo)

            self.assertFalse(report.ok)
            self.assertIn("missing_provenance", {finding.code for finding in report.findings})

    def test_valid_card_and_index_report_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            kb = repo / "knowledge-base"
            create_index(
                kb,
                [
                    {
                        "chunk_id": "chunk-1",
                        "doc_id": "book-1",
                        "title": "Synthetic Book",
                        "source_path": "guide.md",
                        "text": "Retry with an idempotency key.",
                    }
                ],
            )
            add_card(kb, status="candidate")

            report = run_doctor(repo)

            self.assertTrue(report.ok)
            self.assertEqual(report.metrics["cards_total"], 1)
            self.assertEqual(report.metrics["cards_candidate"], 1)
            self.assertEqual(report.metrics["missing_provenance"], 0)


class UtilityEvaluationTests(unittest.TestCase):
    def test_paired_evaluation_passes_all_agreed_thresholds(self) -> None:
        result = evaluate_pairs(CASES, observations(assisted=False), observations(assisted=True))

        self.assertTrue(result.passed, result.failures)
        self.assertGreater(result.metrics["accepted_finding_gain"], 0)
        self.assertEqual(result.metrics["citation_accuracy"], 1.0)
        self.assertEqual(result.metrics["negative_case_violations"], 0)

    def test_false_positive_rate_over_ten_percent_fails(self) -> None:
        result = evaluate_pairs(
            CASES,
            observations(assisted=False),
            observations(assisted=True, false_positives=4),
        )

        self.assertFalse(result.passed)
        self.assertIn("false_positive_rate", result.failures)

    def test_incomplete_or_misaligned_case_set_fails(self) -> None:
        result = evaluate_pairs(CASES, observations(assisted=False)[:-1], observations(assisted=True))

        self.assertFalse(result.passed)
        self.assertIn("case_alignment", result.failures)


if __name__ == "__main__":
    unittest.main()
