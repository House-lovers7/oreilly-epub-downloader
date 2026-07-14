from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from techlib.search import SearchEngine
from tests.kb_fixture import add_card, create_index


CHUNK = {
    "chunk_id": "chunk-1",
    "doc_id": "book-1",
    "title": "Synthetic Book",
    "source_path": "downloads/synthetic.epub",
    "text": "Use an idempotency key when retrying a distributed operation.",
}


class StagedSearchTests(unittest.TestCase):
    def test_active_card_stops_before_fts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            create_index(kb, [CHUNK])
            add_card(kb, status="active")

            result = SearchEngine(kb).search("idempotent retry", domain="architecture")

            self.assertEqual(result.stage, "cards")
            self.assertEqual(result.trace, ["cards"])
            self.assertEqual(result.items[0]["card_id"], "arch-p-001")
            self.assertFalse(result.network_used)

    def test_candidate_card_is_not_automatically_injected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            create_index(kb, [CHUNK])
            add_card(kb, status="candidate")

            result = SearchEngine(kb).search("idempotency retry", domain="architecture")

            self.assertEqual(result.stage, "fts")
            self.assertEqual(result.trace, ["cards", "fts"])
            self.assertEqual(result.items[0]["chunk_id"], "chunk-1")

    def test_no_evidence_is_explicit_and_offline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            create_index(kb)

            result = SearchEngine(kb).search("unrepresented topic")

            self.assertEqual(result.stage, "insufficient_evidence")
            self.assertEqual(result.trace, ["cards", "fts"])
            self.assertEqual(result.items, [])
            self.assertFalse(result.network_used)

    def test_full_section_requires_explicit_chunk_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            create_index(kb, [CHUNK])

            result = SearchEngine(kb).get_section("chunk-1")

            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result["text"], CHUNK["text"])


if __name__ == "__main__":
    unittest.main()
