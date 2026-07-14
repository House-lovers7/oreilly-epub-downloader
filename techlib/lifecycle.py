"""Auditable lifecycle state for distilled knowledge cards."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import tempfile
from pathlib import Path


STATUSES = {"candidate", "active", "deprecated", "archived"}
TRANSITIONS = {
    "candidate": {"active", "deprecated", "archived"},
    "active": {"deprecated"},
    "deprecated": {"candidate", "archived"},
    "archived": {"candidate"},
}
CARD_ID_RE = re.compile(r"^[a-z][a-z0-9-]*-[pat]-\d{3,}$")


class CardLifecycle:
    def __init__(self, path: Path):
        self.path = Path(path)

    def status(self, card_id: str) -> str:
        payload = self._load()
        override = payload["overrides"].get(card_id)
        if isinstance(override, dict):
            return str(override.get("status", payload["default_status"]))
        if isinstance(override, str):
            return override
        return str(payload["default_status"])

    def transition(self, card_id: str, status: str, *, basis: str) -> None:
        if not CARD_ID_RE.fullmatch(card_id):
            raise ValueError("invalid card_id")
        if status not in STATUSES:
            raise ValueError(f"invalid card status: {status}")
        if not basis.strip():
            raise ValueError("a non-empty transition basis is required")
        payload = self._load()
        current = self.status(card_id)
        if current != status and status not in TRANSITIONS[current]:
            raise ValueError(f"invalid card lifecycle transition: {current} -> {status}")
        payload["overrides"][card_id] = {
            "status": status,
            "basis": basis.strip(),
            "recorded_at": dt.datetime.now(dt.UTC).isoformat(),
        }
        self._write(payload)

    def _load(self) -> dict:
        if not self.path.exists():
            return {"version": 1, "default_status": "candidate", "overrides": {}}
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("overrides"), dict):
            raise ValueError("invalid lifecycle registry")
        default = payload.get("default_status", "candidate")
        if default not in STATUSES:
            raise ValueError("invalid default card status")
        payload.setdefault("version", 1)
        payload["default_status"] = default
        return payload

    def _write(self, payload: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)
