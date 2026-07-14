#!/usr/bin/env python3
"""Compatibility entry point for existing Tool Gateway commands."""
from __future__ import annotations

import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from techlib.legacy_cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
