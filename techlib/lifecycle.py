"""Card lifecycle contract (implemented through TDD)."""
from __future__ import annotations

from pathlib import Path


class CardLifecycle:
    def __init__(self, path: Path):
        self.path = Path(path)

    def status(self, card_id: str) -> str:
        return "candidate"

    def transition(self, card_id: str, status: str, *, basis: str) -> None:
        return None
