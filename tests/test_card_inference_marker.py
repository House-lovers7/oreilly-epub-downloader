from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from techlib.search import SearchEngine


def _write_cards(kb: Path, *cards: dict) -> None:
    directory = kb / "cards" / "testing"
    directory.mkdir(parents=True)
    base = {
        "domain": "testing",
        "type": "practice",
        "title": "冪等な再試行",
        "problem": "再試行で処理が重複する",
        "recommendation": "冪等キーを使う",
        "pitfalls": [],
        "keywords": ["再試行"],
        "source_chunks": ["chunk-1"],
        "source_books": ["Synthetic Book"],
        "confidence": "high",
        "status": "active",
    }
    (directory / "practices.jsonl").write_text(
        "".join(json.dumps(dict(base, **c), ensure_ascii=False) + "\n" for c in cards),
        encoding="utf-8",
    )


class InferredWhenNotTests(unittest.TestCase):
    def test_marked_items_are_returned_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            when_not = ["単一プロセス内の計算", "[推論] 再試行が起きない同期バッチ"]
            _write_cards(kb, {"card_id": "test-p-001", "when_not_to_apply": when_not})

            card = SearchEngine(kb).search_cards("再試行")[0]

            self.assertEqual(card["when_not_to_apply"], when_not)
            self.assertEqual(
                card["when_not_to_apply_inferred"], ["[推論] 再試行が起きない同期バッチ"]
            )

    def test_unmarked_card_has_no_inferred_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            _write_cards(
                kb,
                {"card_id": "test-p-001", "when_not_to_apply": ["途中の [推論] は印ではない"]},
            )

            card = SearchEngine(kb).list_cards(domain="testing")[0]

            self.assertNotIn("when_not_to_apply_inferred", card)


if __name__ == "__main__":
    unittest.main()
