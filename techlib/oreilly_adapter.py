"""Approval-gated O'Reilly ingestion adapter.

The adapter has no background mode.  Planning is offline, and execution is
bound to one exact book identifier supplied by the human operator.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.client import OreillyClient
from src.cookie_auth import load_cookies, peek_jwt_expiry
from src.epub import create_epub

from .indexing import IncrementalIndexer, IngestResult


DEFAULT_MAX_BYTES = 512 * 1024 * 1024


@dataclass(frozen=True)
class OreillyIngestPlan:
    book_id: str
    cookie_file: str
    dry_run: bool = True
    network_required: bool = True
    approval_required: bool = True
    max_bytes: int = DEFAULT_MAX_BYTES
    token_expires_at: str | None = None
    token_expired: bool | None = None
    stop_condition: str = "abort before promotion when size or completeness gate fails"


@dataclass(frozen=True)
class OreillyIngestResult:
    book_id: str
    output_path: str
    output_bytes: int
    index: IngestResult


def extract_book_id(value: str) -> str:
    match = re.search(r"learning\.oreilly\.com/library/view/[^/]+/(\d+)", value)
    if match:
        return match.group(1)
    if re.fullmatch(r"\d{10,13}", value):
        return value
    match = re.search(r"(?<!\d)(\d{10,13})(?!\d)", value)
    if match:
        return match.group(1)
    raise ValueError("book must contain a 10-13 digit O'Reilly identifier")


def plan_ingest(book: str, cookie_file: Path, *, max_bytes: int) -> OreillyIngestPlan:
    book_id = extract_book_id(book)
    expiry = peek_jwt_expiry(cookie_file)
    return OreillyIngestPlan(
        book_id=book_id,
        cookie_file=str(cookie_file),
        max_bytes=max_bytes,
        token_expires_at=expiry.isoformat() if expiry else None,
        token_expired=expiry <= dt.datetime.now(dt.UTC) if expiry else None,
    )


def execute_ingest(
    book: str,
    cookie_file: Path,
    *,
    approved_book_id: str,
    downloads_dir: Path,
    kb_dir: Path,
    output: Path | None = None,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> OreillyIngestResult:
    book_id = extract_book_id(book)
    if approved_book_id != book_id:
        raise PermissionError("approval is not bound to the requested book_id")
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")

    session = load_cookies(cookie_file)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    staging = downloads_dir / ".staging"
    staging.mkdir(parents=True, exist_ok=True)
    staged_path = staging / f"{book_id}.epub"
    failure_path = staging / f"{book_id}.failure.json"

    try:
        with OreillyClient(session) as client:
            book_data = client.get_book(book_id)
        create_epub(book_data, staged_path)
        size = staged_path.stat().st_size
        if size > max_bytes:
            raise RuntimeError(
                f"staged EPUB exceeds the approved size ceiling ({size} > {max_bytes})"
            )
        final_path = output or downloads_dir / f"{_safe_filename(book_data.metadata.title)}.epub"
        final_path = final_path if final_path.suffix == ".epub" else final_path.with_suffix(".epub")
        final_path.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged_path, final_path)
        indexed = IncrementalIndexer(kb_dir).ingest(
            final_path, rights="personal-subscription"
        )
        failure_path.unlink(missing_ok=True)
        return OreillyIngestResult(
            book_id=book_id,
            output_path=str(final_path),
            output_bytes=size,
            index=indexed,
        )
    except Exception as error:
        _write_failure_manifest(
            failure_path,
            {
                "book_id": book_id,
                "status": "quarantined",
                "error_type": type(error).__name__,
                "recorded_at": dt.datetime.now(dt.UTC).isoformat(),
            },
        )
        raise


def result_payload(result: OreillyIngestResult) -> dict[str, Any]:
    payload = asdict(result)
    payload["index"]["manifest_path"] = str(result.index.manifest_path)
    return payload


def _safe_filename(name: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    safe = re.sub(r"\s+", " ", safe).strip(" .")
    return (safe or "book")[:120]


def _write_failure_manifest(path: Path, payload: dict[str, Any]) -> None:
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
