"""Public metadata-only telemetry contract (implemented through TDD)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MetadataTelemetry:
    def __init__(self, path: Path):
        self.path = Path(path)

    def record(self, event: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")
