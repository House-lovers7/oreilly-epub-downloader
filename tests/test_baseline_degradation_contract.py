from __future__ import annotations

import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from techlib import legacy_cli
from tests.kb_fixture import add_card


def _cards_args(kb: Path, domain: str) -> Namespace:
    return Namespace(kb_dir=str(kb), domain=domain, type=None, query=None, limit=8)


def _context_pack_args(kb: Path, domain: str, query: str) -> Namespace:
    return Namespace(
        kb_dir=str(kb),
        query=query,
        domain=domain,
        limit=6,
        source_type=None,
        project=None,
        cards_limit=6,
        output=None,
    )


class BaselineDegradationContractTests(unittest.TestCase):
    def test_cards_reports_degraded_when_only_candidate_cards_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            add_card(kb, status="candidate", domain="architecture")

            payload, exit_code = legacy_cli._cards(_cards_args(kb, "architecture"))

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["active_available"], 0)
            self.assertEqual(payload["candidate_available"], 1)
            self.assertEqual(payload["degraded"], ["no_active_cards"])
            # existing keys must stay intact
            self.assertEqual(payload["domain"], "architecture")
            self.assertIn("match_status", payload)
            self.assertIn("reason_code", payload)

    def test_cards_reports_no_degradation_when_active_cards_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            add_card(kb, status="active", domain="architecture")

            payload, exit_code = legacy_cli._cards(_cards_args(kb, "architecture"))

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["active_available"], 1)
            self.assertEqual(payload["degraded"], [])

    def test_context_pack_baseline_cards_reports_active_and_candidate_counts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            add_card(kb, status="candidate", domain="architecture")

            payload, exit_code = legacy_cli._context_pack(
                _context_pack_args(kb, "architecture", "idempotent retry")
            )

            self.assertEqual(exit_code, 0)
            baseline = payload["context_pack"]["baseline_cards"]
            self.assertEqual(baseline["active_count"], 0)
            self.assertEqual(baseline["candidate_count"], 1)
            self.assertEqual(baseline["degraded"], ["no_active_cards"])
            # existing keys must stay intact
            self.assertEqual(baseline["domain"], "architecture")
            self.assertEqual(baseline["status_filter"], "active")
            self.assertIn("cards", baseline)
            self.assertIn("match_status", baseline)

    def test_context_pack_baseline_cards_not_degraded_with_active_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            add_card(kb, status="active", domain="architecture")

            payload, exit_code = legacy_cli._context_pack(
                _context_pack_args(kb, "architecture", "idempotent retry")
            )

            self.assertEqual(exit_code, 0)
            baseline = payload["context_pack"]["baseline_cards"]
            self.assertEqual(baseline["active_count"], 1)
            self.assertEqual(baseline["candidate_count"], 0)
            self.assertEqual(baseline["degraded"], [])


if __name__ == "__main__":
    unittest.main()
