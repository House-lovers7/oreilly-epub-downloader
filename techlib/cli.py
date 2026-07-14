"""CLI contract for techlib (commands implemented through TDD)."""
from __future__ import annotations

import click


@click.group()
def main() -> None:
    """Local technical knowledge supply system."""
