from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from src.client import OreillyClient
from src.cookie_auth import Session, load_cookies
from src.epub import create_epub
from src.models import Book, BookMetadata, Chapter, Image


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


if __name__ == "__main__":
    unittest.main()
