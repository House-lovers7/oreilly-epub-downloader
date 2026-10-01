from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.kb_fixture import create_index

ROOT = Path(__file__).resolve().parents[1]

CHUNKS = [
    ("c1", "d1", "code review is a practice"),
    ("c2", "d1", "the review of code matters"),
    ("c3", "d1", "コードレビューを行う"),  # unicode61 は分かち書きされず、語中一致は FTS に出ない
    ("c4", "d2", "code review outside the allow list"),
]


class DomainPackQueryRecallTests(unittest.TestCase):
    def test_manifest_has_query_recall_with_fts_and_like_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "kb"
            create_index(kb)
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            for did in ("d1", "d2"):
                con.execute("INSERT INTO docs VALUES (?, ?, '[]', 'x.epub', 'epub', '{}')", (did, "Book " + did))
            for cid, did, text in CHUNKS:
                con.execute("INSERT INTO chunks VALUES (?, ?, 's', 0, ?, 'H', 'r.xhtml', 'x.epub', 'epub', ?, ?)",
                            (cid, did, "Book " + did, text, len(text)))
                con.execute("INSERT INTO chunks_fts(chunk_id, doc_id, title, heading, text) VALUES (?, ?, ?, 'H', ?)",
                            (cid, did, "Book " + did, text))
            con.commit(); con.close()
            docs = Path(tmp) / "docs.txt"
            docs.write_text("# allow\nd1\n", encoding="utf-8")
            out = Path(tmp) / "out"
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "domain_pack_filtered.py"), "code-review",
                 "--kb-dir", str(kb), "--docs", str(docs), "--query", "code review", "--query", "レビュー",
                 "--output-dir", str(out)],
                capture_output=True, text=True, check=True)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["chunk_count"], 2)
            self.assertEqual(manifest["doc_filter"], ["d1"])
            self.assertEqual(
                manifest["query_recall"],
                [{"query": "code review", "fts_count": 2, "like_count": 2},
                 {"query": "レビュー", "fts_count": 0, "like_count": 1}],
            )
            self.assertIn("query_recall", json.loads(proc.stdout)["manifest"])


if __name__ == "__main__":
    unittest.main()
