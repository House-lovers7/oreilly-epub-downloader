"""Incremental, content-addressed indexing for owned local documents."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .manifest import build_source_manifest, manifest_is_stale


EXTRACTOR_VERSION = "techlib-extractor-v1"
CHUNKER_VERSION = "heading-aware-chars-v1"
SUPPORTED_SUFFIXES = {".epub", ".md", ".markdown", ".txt", ".pdf"}


@dataclass(frozen=True)
class IngestResult:
    doc_id: str
    title: str
    section_count: int
    chunk_count: int
    changed: bool
    manifest_path: Path


class IncrementalIndexer:
    def __init__(self, kb_dir: Path, *, chunk_chars: int = 5000):
        self.kb_dir = Path(kb_dir)
        self.chunk_chars = chunk_chars

    def ingest(self, source: Path, *, rights: str) -> IngestResult:
        source = Path(source).expanduser().resolve()
        if source.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"unsupported source type: {source.suffix or '<none>'}")
        if not rights.strip():
            raise ValueError("rights classification is required")
        if not source.is_file():
            raise ValueError(f"source is not a regular file: {source}")

        source_manifest = build_source_manifest(
            source, rights=rights.strip(), extractor_version=EXTRACTOR_VERSION
        )
        manifest_path = self._manifest_path(source)
        existing = _read_json(manifest_path)
        if existing and not manifest_is_stale(existing, source):
            doc_id = str(existing.get("doc_id", ""))
            if doc_id and self._doc_exists(doc_id):
                return IngestResult(
                    doc_id=doc_id,
                    title=str(existing.get("title", source.stem)),
                    section_count=int(existing.get("section_count", 0)),
                    chunk_count=int(existing.get("chunk_count", 0)),
                    changed=False,
                    manifest_path=manifest_path,
                )

        title, authors, sections, metadata = self._extract(source)
        sections = [(heading, text) for heading, text in sections if text.strip()]
        if not sections:
            raise RuntimeError("source extraction produced no readable sections")
        doc_id = f"doc-{source_manifest['source_sha256'][:16]}"
        chunks = list(self._make_chunks(doc_id, title, source, sections))
        if not chunks:
            raise RuntimeError("source extraction produced no indexable chunks")

        self._initialize_database()
        db_path = self.kb_dir / "index" / "library.sqlite"
        connection = sqlite3.connect(db_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            old_ids = [
                row[0]
                for row in connection.execute(
                    "SELECT doc_id FROM docs WHERE source_path = ?", (str(source),)
                )
            ]
            for old_id in old_ids:
                connection.execute("DELETE FROM chunks_fts WHERE doc_id = ?", (old_id,))
                connection.execute("DELETE FROM chunks WHERE doc_id = ?", (old_id,))
                connection.execute("DELETE FROM docs WHERE doc_id = ?", (old_id,))

            connection.execute(
                "INSERT OR REPLACE INTO docs VALUES (?, ?, ?, ?, ?, ?)",
                (
                    doc_id,
                    title,
                    json.dumps(authors, ensure_ascii=False),
                    str(source),
                    source.suffix.lower().lstrip("."),
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )
            for chunk in chunks:
                connection.execute(
                    "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        chunk["chunk_id"],
                        doc_id,
                        chunk["section_id"],
                        chunk["chunk_order"],
                        title,
                        chunk["heading"],
                        chunk["source_ref"],
                        str(source),
                        source.suffix.lower().lstrip("."),
                        chunk["text"],
                        len(chunk["text"]),
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO chunks_fts(chunk_id, doc_id, title, heading, text)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        chunk["chunk_id"],
                        doc_id,
                        title,
                        chunk["heading"],
                        chunk["text"],
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        manifest = {
            **source_manifest,
            "doc_id": doc_id,
            "title": title,
            "authors": authors,
            "source_type": source.suffix.lower().lstrip("."),
            "section_count": len(sections),
            "chunk_count": len(chunks),
            "chunker_version": CHUNKER_VERSION,
            "embedding_status": "deferred",
            "complete": True,
        }
        _atomic_write_json(manifest_path, manifest)
        self._update_catalog(doc_id, title, authors, source, len(sections), len(chunks), metadata)
        return IngestResult(
            doc_id=doc_id,
            title=title,
            section_count=len(sections),
            chunk_count=len(chunks),
            changed=True,
            manifest_path=manifest_path,
        )

    def _manifest_path(self, source: Path) -> Path:
        import hashlib

        path_id = hashlib.sha256(str(source).encode("utf-8")).hexdigest()[:16]
        return self.kb_dir / "manifests" / f"{path_id}.json"

    def _doc_exists(self, doc_id: str) -> bool:
        db = self.kb_dir / "index" / "library.sqlite"
        if not db.exists():
            return False
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as connection:
            return connection.execute(
                "SELECT 1 FROM docs WHERE doc_id = ?", (doc_id,)
            ).fetchone() is not None

    def _extract(
        self, source: Path
    ) -> tuple[str, list[str], list[tuple[str, str]], dict[str, Any]]:
        suffix = source.suffix.lower()
        if suffix in {".md", ".markdown"}:
            return self._extract_markdown(source)
        if suffix == ".txt":
            text = _normalize_text(source.read_text(encoding="utf-8", errors="replace"))
            return source.stem, [], [(source.stem, text)], {}
        if suffix == ".epub":
            return self._extract_epub(source)
        if suffix == ".pdf":
            return self._extract_pdf(source)
        raise ValueError(f"unsupported source type: {suffix}")

    @staticmethod
    def _extract_markdown(
        source: Path,
    ) -> tuple[str, list[str], list[tuple[str, str]], dict[str, Any]]:
        text = source.read_text(encoding="utf-8", errors="replace")
        title = source.stem
        sections: list[tuple[str, str]] = []
        heading = title
        buffer: list[str] = []
        for line in text.splitlines():
            match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
            if match:
                if buffer:
                    sections.append((heading, _normalize_text("\n".join(buffer))))
                heading = match.group(1).strip()
                if not sections and heading:
                    title = heading
                buffer = []
            else:
                buffer.append(line)
        if buffer:
            sections.append((heading, _normalize_text("\n".join(buffer))))
        return title, [], sections, {}

    @staticmethod
    def _extract_epub(
        source: Path,
    ) -> tuple[str, list[str], list[tuple[str, str]], dict[str, Any]]:
        from bs4 import BeautifulSoup
        from ebooklib import ITEM_DOCUMENT, epub

        book = epub.read_epub(str(source), options={"ignore_ncx": True})
        titles = book.get_metadata("DC", "title")
        creators = book.get_metadata("DC", "creator")
        title = str(titles[0][0]) if titles else source.stem
        authors = [str(value) for value, _ in creators]
        sections: list[tuple[str, str]] = []
        for item in book.get_items_of_type(ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "lxml")
            for tag in soup.find_all(["script", "style", "nav"]):
                tag.decompose()
            heading_tag = soup.find(["h1", "h2", "h3"])
            heading = heading_tag.get_text(" ", strip=True) if heading_tag else item.get_name()
            text = _normalize_text(soup.get_text("\n", strip=True))
            if text:
                sections.append((heading, text))
        return title, authors, sections, {"epub_version": str(book.get_metadata("DC", "format"))}

    @staticmethod
    def _extract_pdf(
        source: Path,
    ) -> tuple[str, list[str], list[tuple[str, str]], dict[str, Any]]:
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "PDF support is conditional; install pypdf for text-layer PDFs"
            ) from error
        reader = PdfReader(str(source))
        sections = [
            (f"Page {index}", _normalize_text(page.extract_text() or ""))
            for index, page in enumerate(reader.pages, start=1)
        ]
        metadata = dict(reader.metadata or {})
        return str(metadata.get("/Title") or source.stem), [], sections, metadata

    def _make_chunks(
        self,
        doc_id: str,
        title: str,
        source: Path,
        sections: list[tuple[str, str]],
    ) -> Iterable[dict[str, Any]]:
        del title
        order = 0
        for section_index, (heading, text) in enumerate(sections, start=1):
            section_id = f"sec-{section_index:04d}"
            parts = _split_text(text, self.chunk_chars)
            for part_index, part in enumerate(parts, start=1):
                yield {
                    "chunk_id": f"{doc_id}-{section_id}-{part_index:03d}",
                    "section_id": section_id,
                    "chunk_order": order,
                    "heading": heading,
                    "source_ref": f"{source.name}#{section_id}",
                    "text": part,
                }
                order += 1

    def _initialize_database(self) -> None:
        index = self.kb_dir / "index"
        index.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(index / "library.sqlite") as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS docs (
                    doc_id TEXT PRIMARY KEY,
                    title TEXT,
                    authors_json TEXT,
                    source_path TEXT,
                    source_type TEXT,
                    metadata_json TEXT
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT,
                    section_id TEXT,
                    chunk_order INTEGER,
                    title TEXT,
                    heading TEXT,
                    source_ref TEXT,
                    source_path TEXT,
                    source_type TEXT,
                    text TEXT,
                    char_count INTEGER
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    doc_id UNINDEXED,
                    title,
                    heading,
                    text,
                    tokenize='unicode61'
                );
                """
            )

    def _update_catalog(
        self,
        doc_id: str,
        title: str,
        authors: list[str],
        source: Path,
        section_count: int,
        chunk_count: int,
        metadata: dict[str, Any],
    ) -> None:
        path = self.kb_dir / "catalog.json"
        catalog = _read_json(path) or []
        if not isinstance(catalog, list):
            catalog = catalog.get("docs", []) if isinstance(catalog, dict) else []
        source_path = str(source)
        catalog = [row for row in catalog if row.get("source_path") != source_path]
        catalog.append(
            {
                "doc_id": doc_id,
                "title": title,
                "authors": authors,
                "source_path": source_path,
                "source_type": source.suffix.lower().lstrip("."),
                "section_count": section_count,
                "chunk_count": chunk_count,
                "metadata": metadata,
            }
        )
        catalog.sort(key=lambda row: (str(row.get("title", "")).casefold(), row.get("doc_id", "")))
        _atomic_write_json(path, catalog)


def _split_text(text: str, limit: int) -> list[str]:
    if limit < 64:
        raise ValueError("chunk_chars must be at least 64")
    text = _normalize_text(text)
    if len(text) <= limit:
        return [text] if text else []
    parts: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            parts.append(remaining)
            break
        boundary = max(remaining.rfind("。", 0, limit), remaining.rfind(". ", 0, limit))
        if boundary < limit // 2:
            boundary = remaining.rfind(" ", 0, limit)
        if boundary < limit // 2:
            boundary = limit
        else:
            boundary += 1
        parts.append(remaining[:boundary].strip())
        remaining = remaining[boundary:].strip()
    return [part for part in parts if part]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
