from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from techlib.distillation import build_domain_pack
from techlib.lifecycle import CardLifecycle
from tests.kb_fixture import add_card, create_index


class DistillationTests(unittest.TestCase):
    def test_domain_pack_is_explicit_atomic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "knowledge-base"
            create_index(
                kb,
                [
                    {
                        "chunk_id": "chunk-1",
                        "doc_id": "book-1",
                        "title": "Retry Guide",
                        "source_path": "guide.md",
                        "text": "Retry with an idempotency key.",
                    }
                ],
            )

            first = build_domain_pack(kb, "architecture", ["idempotency retry"])
            second = build_domain_pack(kb, "architecture", ["idempotency retry"])

            self.assertEqual(first.chunk_count, 1)
            self.assertEqual(second.chunk_count, 1)
            rows = first.pack_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 1)
            self.assertEqual(json.loads(rows[0])["chunk_id"], "chunk-1")
            self.assertTrue(first.manifest_path.exists())


class GatewayCompatibilityTests(unittest.TestCase):
    SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "technical_library.py"

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.SCRIPT), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_candidate_card_is_hidden_from_gateway_compatibility_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "knowledge-base"
            create_index(kb)
            add_card(kb, status="candidate")

            result = self.run_script(
                "cards",
                "architecture",
                "--kb-dir",
                str(kb),
                "--query",
                "idempotency retry",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["cards"], [])
            self.assertEqual(payload["candidate_available"], 1)
            self.assertEqual(payload["match_status"], "insufficient_active_evidence")

    def test_active_card_is_returned_without_opening_the_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "knowledge-base"
            create_index(kb)
            add_card(kb, status="candidate")
            CardLifecycle(kb / "cards" / "lifecycle.json").transition(
                "arch-p-001", "active", basis="paired eval passed"
            )

            result = self.run_script(
                "cards",
                "architecture",
                "--kb-dir",
                str(kb),
                "--query",
                "idempotency retry",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["cards"][0]["card_id"], "arch-p-001")
            self.assertEqual(payload["match_status"], "matched")

    def test_search_command_uses_local_progressive_engine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "knowledge-base"
            create_index(
                kb,
                [
                    {
                        "chunk_id": "chunk-1",
                        "doc_id": "book-1",
                        "title": "Retry Guide",
                        "source_path": "guide.md",
                        "text": "Retry with an idempotency key.",
                    }
                ],
            )

            result = self.run_script(
                "search", "idempotency retry", "--kb-dir", str(kb)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["retrieval"]["stage"], "fts")
            self.assertFalse(payload["retrieval"]["network_used"])
            self.assertEqual(payload["results"][0]["chunk_id"], "chunk-1")


if __name__ == "__main__":
    unittest.main()
