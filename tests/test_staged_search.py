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

    def test_fts_relaxes_all_term_match_without_accepting_single_generic_term(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            create_index(
                kb,
                [
                    {
                        "chunk_id": "chunk-1",
                        "doc_id": "book-1",
                        "title": "Retry Guide",
                        "source_path": "guide.md",
                        "text": "Idempotency makes a retry safe after partial failure.",
                    },
                    {
                        "chunk_id": "chunk-2",
                        "doc_id": "book-2",
                        "title": "Generic Guide",
                        "source_path": "generic.md",
                        "text": "A system can have many unrelated properties.",
                    },
                ],
            )

            result = SearchEngine(kb).search(
                "idempotency retry distributed system consistency", limit=5
            )

            self.assertEqual(result.stage, "fts")
            self.assertEqual([item["chunk_id"] for item in result.items], ["chunk-1"])
            self.assertEqual(result.items[0]["retrieval_mode"], "relaxed_or")


if __name__ == "__main__":
    unittest.main()
