#!/usr/bin/env python3
"""Install or roll back the thin Tool Gateway bridge; dry-run by default."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


LEGACY_ASSIGNMENT = (
    'TECH_LIBRARY_SCRIPT = ROOT / "_technical_library" / "technical_library.py"'
)
BRIDGE_ASSIGNMENT = """TECH_LIBRARY_SCRIPT = (
    ROOT / "oreilly-epub-downloader" / "scripts" / "technical_library.py"
)"""
DEFAULT_GATEWAY = (
    Path(__file__).resolve().parents[2] / "_tool_gateway" / "tool_gateway.py"
)


def configure_bridge(
    gateway: Path, *, write: bool, rollback: bool = False
) -> dict[str, object]:
    """Safely switch exactly one known assignment and reject unknown layouts."""
    gateway = Path(gateway).expanduser().resolve()
    text = gateway.read_text(encoding="utf-8")
    current = BRIDGE_ASSIGNMENT if rollback else LEGACY_ASSIGNMENT
    target = LEGACY_ASSIGNMENT if rollback else BRIDGE_ASSIGNMENT
    action = "rollback" if rollback else "install"

    if target in text:
        return {
            "ok": True,
            "action": action,
            "gateway": str(gateway),
            "change_required": False,
            "changed": False,
            "dry_run": not write,
        }
    if text.count(current) != 1:
        raise RuntimeError(
            "gateway assignment is unknown or ambiguous; refusing a broad rewrite"
        )

    result = {
        "ok": True,
        "action": action,
        "gateway": str(gateway),
        "change_required": True,
        "changed": False,
        "dry_run": not write,
    }
    if not write:
        return result

    updated = text.replace(current, target, 1)
    _atomic_write(gateway, updated)
    result["changed"] = True
    result["dry_run"] = False
    return result


def _atomic_write(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gateway", type=Path, default=DEFAULT_GATEWAY)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    try:
        result = configure_bridge(
            args.gateway, write=args.write, rollback=args.rollback
        )
    except (OSError, RuntimeError) as error:
        parser.exit(1, f"gateway bridge: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
