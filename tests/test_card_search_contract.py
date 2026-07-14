from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class CardSearchContractTests(unittest.TestCase):
    def test_unmatched_query_returns_no_cards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            cards_dir = kb / "cards" / "architecture"
            cards_dir.mkdir(parents=True)
            card = {
                "card_id": "arch-p-001",
                "domain": "architecture",
                "type": "practice",
                "title": "Idempotent retry",
                "problem": "Retries can duplicate work",
                "recommendation": "Use idempotency keys",
                "pitfalls": ["Unbounded retries"],
                "when_not_to_apply": ["Pure computation"],
                "keywords": ["retry", "idempotency"],
                "source_chunks": ["chunk-1"],
                "source_books": ["Synthetic Book"],
                "confidence": "high",
            }
            (cards_dir / "practices.jsonl").write_text(
                json.dumps(card) + "\n", encoding="utf-8"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "technical_library.py"),
                    "cards",
                    "architecture",
                    "--kb-dir",
                    str(kb),
                    "--query",
                    "unrelated quantum gardening",
                    "--limit",
                    "3",
                ],
                cwd=REPO,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["cards"], [])
            self.assertEqual(payload["match_status"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
