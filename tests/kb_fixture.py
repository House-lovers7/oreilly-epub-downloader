from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def create_index(kb: Path, rows: list[dict] | None = None) -> None:
    index_dir = kb / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(index_dir / "library.sqlite")
    con.executescript(
        """
        CREATE TABLE docs (
            doc_id TEXT PRIMARY KEY,
            title TEXT,
            authors_json TEXT,
            source_path TEXT,
            source_type TEXT,
            metadata_json TEXT
        );
        CREATE TABLE chunks (
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
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            chunk_id UNINDEXED,
            doc_id UNINDEXED,
            title,
            heading,
            text,
            tokenize='unicode61'
        );
        """
    )
    for row in rows or []:
        con.execute(
            "INSERT INTO docs VALUES (?, ?, ?, ?, ?, ?)",
            (
                row["doc_id"],
                row["title"],
                "[]",
                row["source_path"],
                "epub",
                "{}",
            ),
        )
        values = (
            row["chunk_id"],
            row["doc_id"],
            row.get("section_id", "section-1"),
            row.get("chunk_order", 0),
            row["title"],
            row.get("heading", "Heading"),
            row.get("source_ref", "chapter.xhtml"),
            row["source_path"],
            "epub",
            row["text"],
            len(row["text"]),
        )
        con.execute("INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
        con.execute(
            "INSERT INTO chunks_fts(chunk_id, doc_id, title, heading, text) VALUES (?, ?, ?, ?, ?)",
            (row["chunk_id"], row["doc_id"], row["title"], row.get("heading", "Heading"), row["text"]),
        )
    con.commit()
    con.close()


def add_card(kb: Path, *, status: str, domain: str = "architecture") -> None:
    directory = kb / "cards" / domain
    directory.mkdir(parents=True, exist_ok=True)
    card = {
        "card_id": "arch-p-001",
        "domain": domain,
        "type": "practice",
        "title": "Idempotent retry",
        "problem": "Retries can duplicate work",
        "recommendation": "Use idempotency keys",
        "pitfalls": ["Unbounded retries"],
        "when_not_to_apply": ["Pure local computation"],
        "keywords": ["retry", "idempotency"],
        "source_chunks": ["chunk-1"],
        "source_books": ["Synthetic Book"],
        "confidence": "high",
        "status": status,
    }
    (directory / "practices.jsonl").write_text(
        json.dumps(card) + "\n", encoding="utf-8"
    )
