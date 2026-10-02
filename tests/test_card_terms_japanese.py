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


class CardTieBreakTests(unittest.TestCase):
    def test_title_match_ranks_before_body_only_match_at_same_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            directory = kb / "cards" / "testing"
            directory.mkdir(parents=True)
            base = {
                "domain": "testing",
                "type": "practice",
                "pitfalls": ["p"],
                "when_not_to_apply": ["w"],
                "keywords": ["k"],
                "source_chunks": ["chunk-1"],
                "source_books": ["Synthetic Book"],
                "confidence": "high",
                "status": "active",
            }
            body_only = dict(base, card_id="test-p-001", title="仕様を共有する",
                             problem="テストの自動化が進まない", recommendation=["契約を公開する"])
            in_title = dict(base, card_id="test-p-002", title="テストの自動化を段階的に進める",
                            problem="手作業の確認が多い", recommendation=["単体から自動化する"])
            (directory / "practices.jsonl").write_text(
                "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in (body_only, in_title)),
                encoding="utf-8",
            )

            items = SearchEngine(kb).search_cards("テストの自動化")

            self.assertEqual([c["card_id"] for c in items], ["test-p-002", "test-p-001"])
            self.assertEqual([c["match_score"] for c in items], [1.0, 1.0])


if __name__ == "__main__":
    unittest.main()
