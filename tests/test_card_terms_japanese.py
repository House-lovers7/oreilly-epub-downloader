from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from techlib.search import SearchEngine, _card_terms, _safe_fts_query


def _write_card(kb: Path, *, status: str = "active") -> None:
    directory = kb / "cards" / "observability"
    directory.mkdir(parents=True, exist_ok=True)
    card = {
        "card_id": "obs-p-001",
        "domain": "observability",
        "type": "practice",
        "title": "アラートは緊急度で分類し、重複する通知は抑制する",
        "problem": "依存先の障害で同じ通知が大量に届く",
        "recommendation": "緊急度ごとに通知先を分ける",
        "pitfalls": ["すべてをページングする"],
        "when_not_to_apply": ["小規模な単一サービス"],
        "keywords": ["alert", "アラート"],
        "source_chunks": ["chunk-1"],
        "source_books": ["Synthetic Book"],
        "confidence": "high",
        "status": status,
    }
    (directory / "practices.jsonl").write_text(
        json.dumps(card, ensure_ascii=False) + "\n", encoding="utf-8"
    )


class CardTermsJapaneseTests(unittest.TestCase):
    def test_compound_is_split_at_particle(self) -> None:
        self.assertEqual(_card_terms("アラートの抑制"), ["アラート", "抑制"])
        self.assertEqual(
            _card_terms("デプロイパイプラインの自動化"), ["デプロイパイプライン", "自動化"]
        )
        self.assertEqual(_card_terms("APIのバージョニング"), ["api", "バージョニング"])
        self.assertEqual(_card_terms("キャッシュを使う"), ["キャッシュ", "使う"])

    def test_okurigana_and_hiragana_words_stay_intact(self) -> None:
        self.assertEqual(_card_terms("書き換え"), ["書き換え"])
        self.assertEqual(_card_terms("リスト内包表記"), ["リスト内包表記"])
        self.assertEqual(_card_terms("alert suppression"), ["alert", "suppression"])

    def test_fts_query_terms_are_unchanged(self) -> None:
        self.assertEqual(_safe_fts_query("アラートの抑制"), '"アラートの抑制"*')

    def test_compound_query_matches_active_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            _write_card(kb)

            result = SearchEngine(kb).search("アラートの抑制")

            self.assertEqual(result.stage, "cards")
            self.assertEqual(result.reason, "active_card_match")
            self.assertEqual(result.items[0]["card_id"], "obs-p-001")
            self.assertEqual(result.items[0]["match_score"], 1.0)

    def test_compound_query_does_not_surface_candidate_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            _write_card(kb, status="candidate")

            self.assertEqual(SearchEngine(kb).search_cards("アラートの抑制"), [])


if __name__ == "__main__":
    unittest.main()
