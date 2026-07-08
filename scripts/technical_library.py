#!/usr/bin/env python3
"""Convenience wrapper for the generic technical library builder."""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "_technical_library" / "technical_library.py"

if __name__ == "__main__":
    sys.argv[0] = str(SCRIPT)
    runpy.run_path(str(SCRIPT), run_name="__main__")
