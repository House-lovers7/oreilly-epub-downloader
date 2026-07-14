"""Metadata-only, append-only telemetry with a narrow privacy contract."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any


ALLOWED_FIELDS = {
    "event",
    "stage",
    "result_count",
    "card_ids",
    "chunk_ids",
    "accepted",
    "duration_ms",
    "cache_hit",
    "domain",
    "outcome",
    "reason_code",
}
FORBIDDEN_FIELDS = {
    "query",
    "prompt",
    "output",
    "excerpt",
    "text",
    "content",
    "cookie",
    "cookies",
    "token",
    "password",
    "secret",
}
SAFE_VALUE_RE = re.compile(r"^[a-zA-Z0-9_.:-]{1,96}$")


class MetadataTelemetry:
    def __init__(self, path: Path, *, rotate_bytes: int = 10 * 1024 * 1024):
        self.path = Path(path)
        self.rotate_bytes = rotate_bytes

    def record(self, event: dict[str, Any]) -> None:
        unknown = set(event) - ALLOWED_FIELDS
        forbidden = set(event) & FORBIDDEN_FIELDS
        if forbidden:
            raise ValueError(
                "telemetry contains forbidden raw fields: " + ", ".join(sorted(forbidden))
            )
        if unknown:
            raise ValueError(
                "telemetry contains fields outside the metadata contract: "
                + ", ".join(sorted(unknown))
            )
        self._validate_values(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._rotate_if_needed()
        payload = dict(event)
        payload["recorded_at"] = dt.datetime.now(dt.UTC).isoformat()
        line = (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(descriptor, line)
        finally:
            os.close(descriptor)
        self.path.chmod(0o600)

    @staticmethod
    def _validate_values(event: dict[str, Any]) -> None:
        for field in ("event", "stage", "domain", "outcome", "reason_code"):
            value = event.get(field)
            if value is not None and (
                not isinstance(value, str) or not SAFE_VALUE_RE.fullmatch(value)
            ):
                raise ValueError(f"telemetry field {field} is not a safe identifier")
        for field in ("card_ids", "chunk_ids"):
            value = event.get(field)
            if value is not None and (
                not isinstance(value, list)
                or not all(isinstance(item, str) and SAFE_VALUE_RE.fullmatch(item) for item in value)
            ):
                raise ValueError(f"telemetry field {field} must contain safe identifiers")

    def _rotate_if_needed(self) -> None:
        if not self.path.exists() or self.path.stat().st_size < self.rotate_bytes:
            return
        stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
        rotated = self.path.with_name(f"{self.path.stem}-{stamp}{self.path.suffix}")
        os.replace(self.path, rotated)
