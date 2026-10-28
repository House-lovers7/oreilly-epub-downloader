from __future__ import annotations

import base64
import datetime as dt
import json
import os
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import httpx
from click.testing import CliRunner

from src.cli import main as legacy_main
from src.client import OreillyClient
from src.cookie_auth import Session, load_cookies
from src.epub import create_epub
from src.models import Book, BookMetadata, Chapter, Image
from techlib.indexing import CitedDocumentError, IncrementalIndexer
from techlib.oreilly_adapter import execute_ingest, plan_ingest


def jwt_with_expiry(expiry: dt.datetime) -> str:
    """Build a signature-free JWT carrying only the ``exp`` claim."""
    payload = (
        base64.urlsafe_b64encode(
            json.dumps({"exp": int(expiry.timestamp())}).encode("utf-8")
        )
        .decode("utf-8")
        .rstrip("=")
    )
    return f"header.{payload}.signature"


def cli_text(result) -> str:
    """Read a CliRunner result across click's stderr split."""
    try:
        return result.output + result.stderr
    except ValueError:
        return result.output


def write_cookie_file(directory: Path, token: str, *, mode: int = 0o600) -> Path:
    cookie_file = directory / "cookies.json"
    cookie_file.write_text(json.dumps({"orm-jwt": token}), encoding="utf-8")
    os.chmod(cookie_file, mode)
    return cookie_file


def sample_metadata(*, language: str = "en") -> BookMetadata:
    return BookMetadata(
        id="book-id",
        title="Synthetic Book",
        authors=["Test Author"],
        publisher="Test Publisher",
        description="Synthetic test fixture",
        cover_url="",
        language=language,
    )


class CookieBoundaryTests(unittest.TestCase):
    def test_cookie_is_not_attached_to_third_party_requests(self) -> None:
        client = OreillyClient(Session({"orm-jwt": "DUMMY_TOKEN"}))
        self.addCleanup(client.close)

        first_party = client.http.build_request(
            "GET", "https://learning.oreilly.com/api/v2/epubs/example/"
        )
        third_party = client.http.build_request(
            "GET", "https://third-party.invalid/image.png"
        )

        self.assertEqual(first_party.headers.get("cookie"), "orm-jwt=DUMMY_TOKEN")
        self.assertIsNone(third_party.headers.get("cookie"))

    def test_cookie_file_rejects_group_or_world_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = Path(tmp) / "cookies.json"
            cookie_file.write_text('{"orm-jwt":"DUMMY_TOKEN"}', encoding="utf-8")
            cookie_file.chmod(0o644)

            with self.assertRaises(PermissionError):
                load_cookies(cookie_file)


class CookieExportShapeTests(unittest.TestCase):
    """A console-copied export carries one extra layer of JSON encoding."""

    @staticmethod
    def write_raw_cookie_file(directory: Path, content: str) -> Path:
        cookie_file = directory / "cookies.json"
        cookie_file.write_text(content, encoding="utf-8")
        os.chmod(cookie_file, 0o600)
        return cookie_file

    def test_double_encoded_export_is_recovered(self) -> None:
        export = json.dumps({"orm-jwt": "DUMMY_TOKEN"})

        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = self.write_raw_cookie_file(Path(tmp), json.dumps(export))

            self.assertEqual(
                load_cookies(cookie_file).cookies, {"orm-jwt": "DUMMY_TOKEN"}
            )

    def test_plain_string_content_is_still_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = self.write_raw_cookie_file(
                Path(tmp), json.dumps("orm-jwt=DUMMY_TOKEN")
            )

            with self.assertRaisesRegex(ValueError, "Invalid cookie file format"):
                load_cookies(cookie_file)

    def test_further_encoding_layers_are_not_unwrapped(self) -> None:
        # Unwrapping repeatedly would accept files no browser export produces.
        export = json.dumps(json.dumps(json.dumps({"orm-jwt": "DUMMY_TOKEN"})))

        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = self.write_raw_cookie_file(Path(tmp), export)

            with self.assertRaisesRegex(ValueError, "Invalid cookie file format"):
                load_cookies(cookie_file)


class TokenFreshnessTests(unittest.TestCase):
    """An expired subscription token must fail before the first request."""

    def test_expired_token_is_rejected_without_network_access(self) -> None:
        stale = dt.datetime.now(dt.UTC) - dt.timedelta(minutes=9)

        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = write_cookie_file(Path(tmp), jwt_with_expiry(stale))

            with self.assertRaisesRegex(PermissionError, "expired at"):
                load_cookies(cookie_file)

    def test_unexpired_token_is_accepted(self) -> None:
        fresh = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=30)

        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = write_cookie_file(Path(tmp), jwt_with_expiry(fresh))

            self.assertIn("orm-jwt", load_cookies(cookie_file).cookies)

    def test_opaque_token_is_treated_as_unknown_expiry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = write_cookie_file(Path(tmp), "DUMMY_TOKEN")

            self.assertIn("orm-jwt", load_cookies(cookie_file).cookies)

    def test_plan_reports_stale_token_without_raising(self) -> None:
        stale = dt.datetime.now(dt.UTC) - dt.timedelta(minutes=9)

        with tempfile.TemporaryDirectory() as tmp:
            # A cookie file execution would reject must still yield a plan.
            cookie_file = write_cookie_file(
                Path(tmp), jwt_with_expiry(stale), mode=0o644
            )

            plan = plan_ingest("9780000000000", cookie_file, max_bytes=1024)

        self.assertTrue(plan.dry_run)
        self.assertTrue(plan.token_expired)
        expected = stale.replace(microsecond=0).isoformat()
        self.assertEqual(plan.token_expires_at, expected)

    def test_plan_reports_unknown_expiry_for_opaque_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = write_cookie_file(Path(tmp), "DUMMY_TOKEN")

            plan = plan_ingest("9780000000000", cookie_file, max_bytes=1024)

        self.assertIsNone(plan.token_expired)
        self.assertIsNone(plan.token_expires_at)


class CliErrorSurfaceTests(unittest.TestCase):
    def test_http_error_is_reported_as_a_cli_error(self) -> None:
        book_id = "9780000000000"

        with tempfile.TemporaryDirectory() as tmp:
            cookie_file = write_cookie_file(Path(tmp), "DUMMY_TOKEN")

            with patch(
                "src.cli.execute_ingest",
                side_effect=httpx.HTTPStatusError(
                    "401 Unauthorized",
                    request=httpx.Request("GET", "https://learning.oreilly.com/"),
                    response=httpx.Response(401),
                ),
            ):
                result = CliRunner().invoke(
                    legacy_main,
                    [
                        book_id,
                        "--cookies",
                        str(cookie_file),
                        "--execute",
                        "--approve-book-id",
                        book_id,
                    ],
                )

        self.assertEqual(result.exit_code, 1)
        self.assertNotIsInstance(result.exception, httpx.HTTPError)
        self.assertIn("401 Unauthorized", cli_text(result))


class ClientCompletenessTests(unittest.TestCase):
    def make_client(self, handler) -> OreillyClient:
        client = OreillyClient(Session({"orm-jwt": "DUMMY_TOKEN"}))
        client.http.close()
        client.http = httpx.Client(
            transport=httpx.MockTransport(handler),
            cookies=Session({"orm-jwt": "DUMMY_TOKEN"}).to_cookie_jar(),
        )
        self.addCleanup(client.close)
        return client

    def test_chapter_api_pagination_is_followed(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.params.get("page") == "2":
                return httpx.Response(
                    200,
                    json={
                        "results": [
                            {
                                "title": "Second",
                                "content_url": "https://learning.oreilly.com/second.html",
                                "ourn": "urn:orm:chapter:second.html",
                            }
                        ],
                        "next": None,
                    },
                )
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "title": "First",
                            "content_url": "https://learning.oreilly.com/first.html",
                            "ourn": "urn:orm:chapter:first.html",
                        }
                    ],
                    "next": "https://learning.oreilly.com/api/v2/epub-chapters/?page=2",
                },
            )

        client = self.make_client(handler)
        with patch("src.client.human_delay"):
            chapters = client._get_chapters("book-id")

        self.assertEqual([chapter.title for chapter in chapters], ["First", "Second"])

    def test_failed_required_chapter_aborts_download(self) -> None:
        client = self.make_client(
            lambda request: httpx.Response(503, request=request, text="unavailable")
        )
        chapters = [
            Chapter(
                id="required",
                title="Required",
                url="",
                content_url="https://learning.oreilly.com/required.html",
                order=0,
            )
        ]

        with patch("src.client.human_delay"), self.assertRaisesRegex(
            RuntimeError, "incomplete"
        ):
            client._fetch_chapter_content(chapters)

    def test_same_basename_images_receive_unique_local_paths(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                request=request,
                content=b"synthetic-image",
                headers={"content-type": "image/png"},
            )

        client = self.make_client(handler)
        chapter = Chapter(
            id="images",
            title="Images",
            url="",
            content_url="https://learning.oreilly.com/images.html",
            order=0,
            html_content=(
                '<p><img src="https://cdn-a.invalid/figure.png"/>'
                '<img src="https://cdn-b.invalid/figure.png"/></p>'
            ),
        )

        with patch("src.client.human_delay"):
            images = client._fetch_images([chapter])

        filenames = [image.filename for image in images.values()]
        self.assertEqual(len(filenames), len(set(filenames)))
        for filename in filenames:
            self.assertIn(filename, chapter.html_content)


class EpubCompletenessTests(unittest.TestCase):
    def test_required_chapter_without_content_rejects_book(self) -> None:
        book = Book(
            metadata=sample_metadata(),
            chapters=[
                Chapter(
                    id="ok",
                    title="Complete",
                    url="",
                    content_url="https://learning.oreilly.com/complete.html",
                    order=0,
                    html_content=(
                        "<p>Complete synthetic chapter with enough deterministic "
                        "fixture text to pass the legacy length filter.</p>"
                    ),
                ),
                Chapter(
                    id="missing",
                    title="Missing",
                    url="",
                    content_url="https://learning.oreilly.com/missing.html",
                    order=1,
                    html_content="",
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "book.epub"
            with self.assertRaisesRegex(RuntimeError, "incomplete"):
                create_epub(book, output)
            self.assertFalse(output.exists())

    def test_duplicate_image_filenames_do_not_create_duplicate_zip_entries(self) -> None:
        book = Book(
            metadata=sample_metadata(),
            chapters=[
                Chapter(
                    id="chapter",
                    title="Chapter",
                    url="",
                    content_url="https://learning.oreilly.com/chapter.html",
                    order=0,
                    html_content=(
                        "<p>Complete synthetic chapter with enough deterministic "
                        "fixture text to pass the legacy length filter.</p>"
                    ),
                )
            ],
            images={
                "https://cdn-a.invalid/figure.png": Image(
                    "https://cdn-a.invalid/figure.png", "images/figure.png", b"one"
                ),
                "https://cdn-b.invalid/figure.png": Image(
                    "https://cdn-b.invalid/figure.png", "images/figure.png", b"two"
                ),
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = create_epub(book, Path(tmp) / "book.epub")
            with zipfile.ZipFile(output) as archive:
                names = archive.namelist()
            self.assertEqual(len(names), len(set(names)))

    def test_chapter_language_matches_book_language(self) -> None:
        book = Book(
            metadata=sample_metadata(language="ja"),
            chapters=[
                Chapter(
                    id="chapter",
                    title="章",
                    url="",
                    content_url="https://learning.oreilly.com/chapter.html",
                    order=0,
                    html_content=(
                        "<p>完全な合成テスト用の章です。既存の長さ判定を通過させ、"
                        "言語属性だけを検証するための十分な長さを持たせています。</p>"
                    ),
                )
            ],
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = create_epub(book, Path(tmp) / "book.epub")
            with zipfile.ZipFile(output) as archive:
                chapter_name = next(
                    name
                    for name in archive.namelist()
                    if name.endswith(".xhtml") and "nav" not in name
                )
                chapter = archive.read(chapter_name).decode("utf-8")
            self.assertIn('lang="ja"', chapter)


class AdapterRefusedIngestTests(unittest.TestCase):
    """execute_ingest keeps the indexed epub in place when the index refuses the new one."""

    book_id = "9780000000000"

    def run_ingest(self, root: Path, *, ingest_error: BaseException | None = None):
        cookie_file = write_cookie_file(root, "DUMMY_TOKEN")
        with patch("techlib.oreilly_adapter.OreillyClient") as client_class, patch(
            "techlib.oreilly_adapter.create_epub",
            side_effect=lambda book, path: Path(path).write_bytes(b"new epub"),
        ), patch("techlib.oreilly_adapter.IncrementalIndexer") as indexer_class:
            client = client_class.return_value.__enter__.return_value
            client.get_book.return_value = Book(metadata=sample_metadata())
            indexer_class.return_value.describes.return_value = False
            if ingest_error is not None:
                indexer_class.return_value.ingest.side_effect = ingest_error
            return execute_ingest(
                self.book_id,
                cookie_file,
                approved_book_id=self.book_id,
                downloads_dir=root / "downloads",
                kb_dir=root / "knowledge-base",
            )

    def test_refused_ingest_restores_the_indexed_epub_and_keeps_the_download(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final_path = root / "downloads" / "Synthetic Book.epub"
            final_path.parent.mkdir(parents=True)
            final_path.write_bytes(b"indexed epub")

            with self.assertRaises(CitedDocumentError):
                self.run_ingest(root, ingest_error=CitedDocumentError("cards cite it"))

            staging = root / "downloads" / ".staging"
            refused_path = staging / f"{self.book_id}.refused.epub"
            self.assertEqual(final_path.read_bytes(), b"indexed epub")
            self.assertEqual(refused_path.read_bytes(), b"new epub")
            self.assertFalse((staging / f"{self.book_id}.previous.epub").exists())
            record = json.loads(
                (staging / f"{self.book_id}.failure.json").read_text(encoding="utf-8")
            )
            self.assertEqual(record["error_type"], "CitedDocumentError")
            self.assertEqual(record["restored_path"], str(final_path))
            self.assertEqual(record["refused_path"], str(refused_path))

    def test_refused_ingest_of_a_new_book_leaves_no_epub_in_downloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            with self.assertRaises(RuntimeError):
                self.run_ingest(root, ingest_error=RuntimeError("no readable sections"))

            staging = root / "downloads" / ".staging"
            self.assertFalse((root / "downloads" / "Synthetic Book.epub").exists())
            self.assertEqual(
                (staging / f"{self.book_id}.refused.epub").read_bytes(), b"new epub"
            )
            record = json.loads(
                (staging / f"{self.book_id}.failure.json").read_text(encoding="utf-8")
            )
            self.assertNotIn("restored_path", record)

    def test_accepted_ingest_replaces_the_epub_and_clears_the_set_aside_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final_path = root / "downloads" / "Synthetic Book.epub"
            final_path.parent.mkdir(parents=True)
            final_path.write_bytes(b"indexed epub")

            result = self.run_ingest(root)

            staging = root / "downloads" / ".staging"
            self.assertEqual(result.output_path, str(final_path))
            self.assertEqual(final_path.read_bytes(), b"new epub")
            self.assertFalse((staging / f"{self.book_id}.previous.epub").exists())
            self.assertFalse((staging / f"{self.book_id}.failure.json").exists())

    def test_leftover_set_aside_epub_stops_before_any_download(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging = root / "downloads" / ".staging"
            staging.mkdir(parents=True)
            previous_path = staging / f"{self.book_id}.previous.epub"
            previous_path.write_bytes(b"indexed epub")
            cookie_file = write_cookie_file(root, "DUMMY_TOKEN")

            with patch("techlib.oreilly_adapter.OreillyClient") as client_class:
                with self.assertRaisesRegex(RuntimeError, "interrupted run"):
                    execute_ingest(
                        self.book_id,
                        cookie_file,
                        approved_book_id=self.book_id,
                        downloads_dir=root / "downloads",
                        kb_dir=root / "knowledge-base",
                    )

            client_class.assert_not_called()
            self.assertEqual(previous_path.read_bytes(), b"indexed epub")

    def test_interrupted_ingest_restores_the_indexed_epub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final_path = root / "downloads" / "Synthetic Book.epub"
            final_path.parent.mkdir(parents=True)
            final_path.write_bytes(b"indexed epub")

            with self.assertRaises(KeyboardInterrupt):
                self.run_ingest(root, ingest_error=KeyboardInterrupt())

            staging = root / "downloads" / ".staging"
            self.assertEqual(final_path.read_bytes(), b"indexed epub")
            self.assertEqual(
                (staging / f"{self.book_id}.refused.epub").read_bytes(), b"new epub"
            )
            self.assertFalse((staging / f"{self.book_id}.previous.epub").exists())
            record = json.loads(
                (staging / f"{self.book_id}.failure.json").read_text(encoding="utf-8")
            )
            self.assertEqual(record["error_type"], "KeyboardInterrupt")


def extract_text_as_one_section(self, source: Path):
    """Stand-in for EPUB extraction: the file's bytes are the book's only section."""
    return "Synthetic Book", [], [("Body", source.read_text(encoding="utf-8"))], {}


class AdapterWithIndexerTests(unittest.TestCase):
    """execute_ingest against the real IncrementalIndexer (only extraction is stubbed)."""

    book_id = "9780000000000"

    def run_ingest(self, root: Path, text: str):
        cookie_file = write_cookie_file(root, "DUMMY_TOKEN")
        with patch("techlib.oreilly_adapter.OreillyClient") as client_class, patch(
            "techlib.oreilly_adapter.create_epub",
            side_effect=lambda book, path: Path(path).write_text(text, encoding="utf-8"),
        ), patch.object(IncrementalIndexer, "_extract", extract_text_as_one_section):
            client = client_class.return_value.__enter__.return_value
            client.get_book.return_value = Book(metadata=sample_metadata())
            return execute_ingest(
                self.book_id,
                cookie_file,
                approved_book_id=self.book_id,
                downloads_dir=root / "downloads",
                kb_dir=root / "knowledge-base",
            )

    @staticmethod
    def doc_ids(root: Path) -> list[str]:
        with sqlite3.connect(root / "knowledge-base" / "index" / "library.sqlite") as connection:
            return [row[0] for row in connection.execute("SELECT doc_id FROM docs")]

    def test_guard_refusal_restores_the_cited_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.run_ingest(root, "first edition text")
            with sqlite3.connect(
                root / "knowledge-base" / "index" / "library.sqlite"
            ) as connection:
                chunk_id = connection.execute("SELECT chunk_id FROM chunks").fetchone()[0]
            cards = root / "knowledge-base" / "cards"
            cards.mkdir()
            (cards / "card.json").write_text(
                json.dumps({"source_chunks": [chunk_id]}), encoding="utf-8"
            )

            with self.assertRaises(CitedDocumentError):
                self.run_ingest(root, "second edition text")

            final_path = Path(first.output_path)
            self.assertEqual(final_path.read_text(encoding="utf-8"), "first edition text")
            self.assertEqual(self.doc_ids(root), [first.index.doc_id])

    def test_failure_after_the_index_commit_keeps_the_new_epub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.run_ingest(root, "first edition text")
            (root / "knowledge-base" / "catalog.json").write_text("{not json", encoding="utf-8")

            with self.assertRaises(ValueError):
                self.run_ingest(root, "second edition text")

            final_path = Path(first.output_path)
            staging = root / "downloads" / ".staging"
            self.assertEqual(final_path.read_text(encoding="utf-8"), "second edition text")
            self.assertNotIn(first.index.doc_id, self.doc_ids(root))
            self.assertEqual(len(self.doc_ids(root)), 1)
            self.assertFalse((staging / f"{self.book_id}.previous.epub").exists())
            self.assertFalse((staging / f"{self.book_id}.refused.epub").exists())
            record = json.loads(
                (staging / f"{self.book_id}.failure.json").read_text(encoding="utf-8")
            )
            self.assertEqual(record["status"], "indexed_metadata_failed")
            self.assertTrue(record["index_updated"])


if __name__ == "__main__":
    unittest.main()
