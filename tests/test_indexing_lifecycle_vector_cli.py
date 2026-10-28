from __future__ import annotations

import io
import json
import os
import sqlite3
import tempfile
import unicodedata
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from click.testing import CliRunner

from src.cli import main as legacy_main
from techlib import legacy_cli
from techlib.cli import main
from techlib.indexing import CitedDocumentError, IncrementalIndexer
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

    def test_changed_source_is_refused_while_cards_cite_prior_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "guide.txt"
            source.write_text("first stable version", encoding="utf-8")
            kb = root / "knowledge-base"
            indexer = IncrementalIndexer(kb)
            first = indexer.ingest(source, rights="owned-local")
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            cited_chunk = con.execute("SELECT chunk_id FROM chunks").fetchone()[0]
            con.close()
            add_card(kb, status="active", overrides={"source_chunks": [cited_chunk]})
            source.write_text("second stable version", encoding="utf-8")

            with self.assertRaises(CitedDocumentError):
                indexer.ingest(source, rights="owned-local")

            con = sqlite3.connect(kb / "index" / "library.sqlite")
            self.assertEqual(con.execute("SELECT doc_id FROM docs").fetchall(), [(first.doc_id,)])
            self.assertEqual(
                con.execute("SELECT text FROM chunks WHERE chunk_id = ?", (cited_chunk,)).fetchone()[0],
                "first stable version",
            )
            con.close()
            manifest = json.loads(first.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["doc_id"], first.doc_id)
            catalog = json.loads((kb / "catalog.json").read_text(encoding="utf-8"))
            self.assertEqual([row["doc_id"] for row in catalog], [first.doc_id])

    def test_ascii_escaped_citation_of_non_ascii_legacy_id_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "guide.txt"
            source.write_text("first stable version", encoding="utf-8")
            kb = root / "knowledge-base"
            indexer = IncrementalIndexer(kb)
            first = indexer.ingest(source, rights="owned-local")
            legacy_id = "デジタル入門-0123456789ab"
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            con.execute("UPDATE docs SET doc_id = ? WHERE doc_id = ?", (legacy_id, first.doc_id))
            con.commit()
            con.close()
            pack = kb / "cards" / "architecture" / "source-pack.jsonl"
            pack.parent.mkdir(parents=True)
            pack.write_text(
                json.dumps({"chunk_id": f"{legacy_id}-sec-0001-000"}, ensure_ascii=True) + "\n",
                encoding="utf-8",
            )
            self.assertNotIn(legacy_id, pack.read_text(encoding="utf-8"))
            source.write_text("second stable version", encoding="utf-8")

            with self.assertRaises(CitedDocumentError):
                indexer.ingest(source, rights="owned-local")

            con = sqlite3.connect(kb / "index" / "library.sqlite")
            self.assertEqual(con.execute("SELECT doc_id FROM docs").fetchall(), [(legacy_id,)])
            con.close()

    def test_citation_in_domain_manifest_json_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "guide.txt"
            source.write_text("first stable version", encoding="utf-8")
            kb = root / "knowledge-base"
            indexer = IncrementalIndexer(kb)
            first = indexer.ingest(source, rights="owned-local")
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            cited_chunk = con.execute("SELECT chunk_id FROM chunks").fetchone()[0]
            con.close()
            manifest = kb / "cards" / "architecture" / "manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps({"domain": "architecture", "chunks": [{"chunk_id": cited_chunk}]}),
                encoding="utf-8",
            )
            source.write_text("second stable version", encoding="utf-8")

            with self.assertRaises(CitedDocumentError):
                indexer.ingest(source, rights="owned-local")

            con = sqlite3.connect(kb / "index" / "library.sqlite")
            self.assertEqual(con.execute("SELECT doc_id FROM docs").fetchall(), [(first.doc_id,)])
            con.close()

    def test_rechunk_of_same_doc_id_is_refused_when_cited_chunk_would_vanish(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "guide.md"
            source.write_text(
                "# Guide\n\n" + " ".join(f"Sentence number {i} is here." for i in range(40)),
                encoding="utf-8",
            )
            kb = root / "knowledge-base"
            first = IncrementalIndexer(kb, chunk_chars=200).ingest(source, rights="owned-local")
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            chunk_ids = [row[0] for row in con.execute("SELECT chunk_id FROM chunks ORDER BY chunk_order")]
            con.close()
            self.assertGreater(len(chunk_ids), 1)
            add_card(kb, status="active", overrides={"source_chunks": [chunk_ids[-1]]})
            # Without the manifest the same bytes are re-processed under the same doc_id.
            first.manifest_path.unlink()

            with self.assertRaises(CitedDocumentError):
                IncrementalIndexer(kb, chunk_chars=5000).ingest(source, rights="owned-local")

            con = sqlite3.connect(kb / "index" / "library.sqlite")
            self.assertEqual(
                [row[0] for row in con.execute("SELECT chunk_id FROM chunks ORDER BY chunk_order")],
                chunk_ids,
            )
            con.close()

    def test_rechunk_of_same_doc_id_keeping_cited_chunks_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "guide.md"
            source.write_text(
                "# Guide\n\n" + " ".join(f"Sentence number {i} is here." for i in range(40)),
                encoding="utf-8",
            )
            kb = root / "knowledge-base"
            indexer = IncrementalIndexer(kb, chunk_chars=200)
            first = indexer.ingest(source, rights="owned-local")
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            cited_chunk = con.execute(
                "SELECT chunk_id FROM chunks ORDER BY chunk_order DESC"
            ).fetchone()[0]
            con.close()
            add_card(kb, status="active", overrides={"source_chunks": [cited_chunk]})
            first.manifest_path.unlink()

            second = indexer.ingest(source, rights="owned-local")

            self.assertTrue(second.changed)
            self.assertEqual(second.doc_id, first.doc_id)
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            self.assertEqual(
                con.execute("SELECT count(*) FROM chunks WHERE chunk_id = ?", (cited_chunk,)).fetchone()[0],
                1,
            )
            con.close()

    def test_legacy_build_reports_a_refused_source_and_indexes_the_rest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources"
            sources.mkdir()
            cited_source = sources / "a-cited.txt"
            cited_source.write_text("first stable version", encoding="utf-8")
            kb = root / "knowledge-base"
            first = IncrementalIndexer(kb).ingest(cited_source, rights="owned-local")
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            cited_chunk = con.execute("SELECT chunk_id FROM chunks").fetchone()[0]
            con.close()
            add_card(kb, status="active", overrides={"source_chunks": [cited_chunk]})
            cited_source.write_text("second stable version", encoding="utf-8")
            (sources / "b-new.txt").write_text("independent new source", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = legacy_cli.main(
                    ["build", "--source-dir", str(sources), "--kb-dir", str(kb), "--rights", "owned-local"]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual([row["source"] for row in payload["refused"]], [str(cited_source.resolve())])
            self.assertIn(cited_chunk, payload["refused"][0]["error"])
            self.assertEqual([doc["title"] for doc in payload["documents"]], ["b-new"])
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            doc_ids = {row[0] for row in con.execute("SELECT doc_id FROM docs")}
            con.close()
            self.assertIn(first.doc_id, doc_ids)
            self.assertIn(payload["documents"][0]["doc_id"], doc_ids)

    def test_legacy_build_skips_the_downloader_staging_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            downloads = root / "downloads"
            staging = downloads / ".staging"
            staging.mkdir(parents=True)
            (downloads / "book.txt").write_text("indexed book", encoding="utf-8")
            (staging / "9780000000000.refused.txt").write_text("refused copy", encoding="utf-8")
            kb = root / "knowledge-base"

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = legacy_cli.main(
                    ["build", "--source-dir", str(downloads), "--kb-dir", str(kb), "--rights", "owned-local"]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["source_count"], 1)
            self.assertEqual([doc["title"] for doc in payload["documents"]], ["book"])

    def test_unreadable_card_file_stops_a_replacing_ingest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "guide.txt"
            source.write_text("first stable version", encoding="utf-8")
            kb = root / "knowledge-base"
            indexer = IncrementalIndexer(kb)
            first = indexer.ingest(source, rights="owned-local")
            broken = kb / "cards" / "architecture" / "practices.jsonl"
            broken.parent.mkdir(parents=True)
            broken.write_text("{not json\n", encoding="utf-8")
            source.write_text("second stable version", encoding="utf-8")

            with self.assertRaises(json.JSONDecodeError):
                indexer.ingest(source, rights="owned-local")

            con = sqlite3.connect(kb / "index" / "library.sqlite")
            self.assertEqual(con.execute("SELECT doc_id FROM docs").fetchall(), [(first.doc_id,)])
            con.close()

    def test_prior_version_stored_under_nfd_path_is_replaced_not_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "デジタル.txt"
            source.write_text("first stable version", encoding="utf-8")
            kb = root / "knowledge-base"
            indexer = IncrementalIndexer(kb)
            indexer.ingest(source, rights="owned-local")
            resolved = str(source.resolve())
            nfd_path = unicodedata.normalize("NFD", resolved)
            self.assertNotEqual(nfd_path, resolved)
            con = sqlite3.connect(kb / "index" / "library.sqlite")
            con.execute("UPDATE docs SET source_path = ?", (nfd_path,))
            con.commit()
            con.close()
            catalog_path = kb / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            for row in catalog:
                row["source_path"] = nfd_path
            catalog_path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(indexer._manifest_path(Path(nfd_path)), indexer._manifest_path(Path(resolved)))
            source.write_text("second stable version", encoding="utf-8")

            second = indexer.ingest(source, rights="owned-local")

            con = sqlite3.connect(kb / "index" / "library.sqlite")
            self.assertEqual(con.execute("SELECT doc_id FROM docs").fetchall(), [(second.doc_id,)])
            con.close()
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual([row["doc_id"] for row in catalog], [second.doc_id])


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

    def test_feedback_command_records_metadata_without_raw_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "knowledge-base"

            result = CliRunner().invoke(
                main,
                [
                    "feedback",
                    "--kb-dir",
                    str(kb),
                    "--card-id",
                    "arch-p-001",
                    "--accepted",
                    "--outcome",
                    "applied",
                    "--duration-ms",
                    "25",
                    "--json",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            event = json.loads(
                (kb / "telemetry" / "events.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(event["event"], "feedback")
            self.assertTrue(event["accepted"])
            self.assertNotIn("query", event)
            self.assertNotIn("output", event)


if __name__ == "__main__":
    unittest.main()
