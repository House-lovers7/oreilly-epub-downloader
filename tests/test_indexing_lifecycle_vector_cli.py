from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from src.cli import main as legacy_main
from techlib.cli import main
from techlib.indexing import IncrementalIndexer
from techlib.lifecycle import CardLifecycle
from techlib.search import SearchEngine
from tests.kb_fixture import add_card, create_index
from tests.test_doctor_evaluation import CASES, observations


class IncrementalIndexerTests(unittest.TestCase):
    def test_markdown_ingest_is_content_addressed_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "guide.md"
            source.write_text(
                "# Retry Guide\n\n## Idempotency\n\nUse an idempotency key before retrying.\n",
                encoding="utf-8",
            )
            kb = root / "knowledge-base"
            indexer = IncrementalIndexer(kb, chunk_chars=80)

            first = indexer.ingest(source, rights="owned-local")
            second = indexer.ingest(source, rights="owned-local")

            self.assertTrue(first.changed)
            self.assertFalse(second.changed)
            self.assertEqual(first.doc_id, second.doc_id)
            self.assertGreater(first.chunk_count, 0)
            self.assertTrue(first.manifest_path.exists())
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            doc_count = con.execute("SELECT count(*) FROM docs").fetchone()[0]
            chunk_count = con.execute("SELECT count(*) FROM chunks").fetchone()[0]
            con.close()
            self.assertEqual(doc_count, 1)
            self.assertEqual(chunk_count, first.chunk_count)

    def test_changed_source_replaces_prior_version_without_duplicate_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "guide.txt"
            source.write_text("first stable version", encoding="utf-8")
            kb = root / "knowledge-base"
            indexer = IncrementalIndexer(kb)
            first = indexer.ingest(source, rights="owned-local")
            source.write_text("second stable version", encoding="utf-8")
            second = indexer.ingest(source, rights="owned-local")

            self.assertNotEqual(first.doc_id, second.doc_id)
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            self.assertEqual(con.execute("SELECT count(*) FROM docs").fetchone()[0], 1)
            self.assertEqual(
                con.execute("SELECT text FROM chunks").fetchone()[0],
                "second stable version",
            )
            con.close()


class CardLifecycleTests(unittest.TestCase):
    def test_transition_requires_basis_and_persists_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lifecycle.json"
            lifecycle = CardLifecycle(path)
            with self.assertRaises(ValueError):
                lifecycle.transition("arch-p-001", "active", basis="")

            lifecycle.transition(
                "arch-p-001", "active", basis="accepted paired evaluation"
            )

            self.assertEqual(lifecycle.status("arch-p-001"), "active")
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["overrides"]["arch-p-001"]["status"], "active")


class LazyVectorTests(unittest.TestCase):
    def test_vector_is_only_called_after_cards_and_fts_are_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            create_index(kb)
            calls: list[tuple[str, int]] = []

            def vector(query: str, limit: int) -> list[dict]:
                calls.append((query, limit))
                return [{"chunk_id": "semantic-1", "score": 0.9}]

            result = SearchEngine(kb, vector_search=vector).search("semantic gap")

            self.assertEqual(result.stage, "vector")
            self.assertEqual(result.trace, ["cards", "fts", "vector"])
            self.assertEqual(calls, [("semantic gap", 5)])


class CliContractTests(unittest.TestCase):
    def test_search_command_returns_structured_json(self) -> None:
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
                        "text": "Idempotency protects a retry operation.",
                    }
                ],
            )
            result = CliRunner().invoke(
                main,
                ["search", "idempotency retry", "--kb-dir", str(kb), "--json"],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            self.assertEqual(payload["stage"], "fts")
            self.assertFalse(payload["network_used"])

    def test_pyproject_exposes_new_and_legacy_commands(self) -> None:
        pyproject = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        self.assertIn('techlib = "techlib.cli:main"', pyproject)
        self.assertIn('oreilly-dl = "src.cli:main"', pyproject)

    def test_oreilly_ingest_is_dry_run_by_default(self) -> None:
        result = CliRunner().invoke(
            main,
            [
                "ingest",
                "oreilly",
                "9780000000000",
                "--cookies",
                "cookies.json",
                "--json",
            ],
        )

        self.assertEqual(result.exit_code, 0, result.output)
        payload = json.loads(result.output)
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["network_required"])
        self.assertEqual(payload["book_id"], "9780000000000")

    def test_oreilly_execute_requires_exact_book_approval(self) -> None:
        result = CliRunner().invoke(
            main,
            [
                "ingest",
                "oreilly",
                "9780000000000",
                "--cookies",
                "cookies.json",
                "--execute",
                "--approve-book-id",
                "9781111111111",
            ],
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("approval", result.output.lower())

    def test_doctor_command_exposes_machine_readable_health(self) -> None:
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
                        "text": "Use an idempotency key.",
                    }
                ],
            )
            add_card(kb, status="candidate")

            result = CliRunner().invoke(
                main, ["doctor", "--repo", str(repo), "--json"]
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["metrics"]["cards_total"], 1)

    def test_eval_score_command_rejects_failed_utility_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "cases": CASES,
                "baseline": observations(assisted=False),
                "assisted": observations(assisted=True, false_positives=4),
            }
            paths: dict[str, Path] = {}
            for name, payload in files.items():
                path = root / f"{name}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths[name] = path

            result = CliRunner().invoke(
                main,
                [
                    "eval",
                    "score",
                    "--cases",
                    str(paths["cases"]),
                    "--baseline",
                    str(paths["baseline"]),
                    "--assisted",
                    str(paths["assisted"]),
                    "--json",
                ],
            )

            self.assertEqual(result.exit_code, 1, result.output)
            payload = json.loads(result.output)
            self.assertFalse(payload["passed"])
            self.assertIn("false_positive_rate", payload["failures"])

    def test_legacy_downloader_is_an_offline_plan_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cookie = Path(tmp) / "cookies.json"
            cookie.write_text("{}", encoding="utf-8")
            os.chmod(cookie, 0o600)

            result = CliRunner().invoke(
                legacy_main,
                ["9780000000000", "--cookies", str(cookie), "--json"],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output)
            self.assertTrue(payload["dry_run"])
            self.assertTrue(payload["approval_required"])


if __name__ == "__main__":
    unittest.main()
