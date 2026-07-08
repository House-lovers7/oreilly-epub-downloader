#!/usr/bin/env python3
"""Validate knowledge-base/cards/project_map.jsonl integrity.

Checks (all must pass; exit 0 with "OK" only when error count is 0):
  1. relevant_domains: each domain has a cards/<domain>/ directory
  2. recommended_practices: each card_id exists in cards/<domain>/{practices,antipatterns,tradeoffs}.jsonl
  3. brief: file exists and its "# PROJECT_BRIEF: <name>" heading matches the
     entry's project name exactly (mismatch is silently ignored by
     load_project_map_entry / parse_project_brief, so we fail loudly here)
  4. relevant_books: each title exists in catalog.json (warning only)
  5. project names are unique
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CARDS = REPO / "knowledge-base" / "cards"
CATALOG = REPO / "knowledge-base" / "catalog.json"
PORTFOLIO_ROOT = REPO.parent  # app_development/ (brief paths are relative to it)

CARD_FILES = ("practices.jsonl", "antipatterns.jsonl", "tradeoffs.jsonl")
DOMAIN_PREFIX = {
    "arch": "architecture", "sre": "sre", "sec": "security", "db": "database",
    "api": "api-design", "net": "networking", "perf": "performance", "test": "testing",
}


def load_card_ids() -> set[str]:
    ids: set[str] = set()
    for domain_dir in CARDS.iterdir():
        if not domain_dir.is_dir():
            continue
        for name in CARD_FILES:
            f = domain_dir / name
            if not f.exists():
                continue
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    ids.add(json.loads(line)["card_id"])
    return ids


def load_catalog_titles() -> set[str]:
    if not CATALOG.exists():
        return set()
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    docs = data.get("docs", data) if isinstance(data, dict) else data
    titles = set()
    for doc in docs:
        if isinstance(doc, dict) and doc.get("title"):
            titles.add(doc["title"])
    return titles


def brief_project_name(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# PROJECT_BRIEF:"):
            return line.split(":", 1)[1].strip()
    return None


def main() -> int:
    pmap = CARDS / "project_map.jsonl"
    if not pmap.exists():
        print(f"ERROR: {pmap} not found")
        return 1

    card_ids = load_card_ids()
    catalog_titles = load_catalog_titles()
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()

    entries = [json.loads(l) for l in pmap.read_text(encoding="utf-8").splitlines() if l.strip()]
    for entry in entries:
        name = entry.get("project", "<missing>")
        prefix = f"[{name}]"

        if name in seen:
            errors.append(f"{prefix} duplicate project name")
        seen.add(name)

        for domain in entry.get("relevant_domains", []):
            if not (CARDS / domain).is_dir():
                errors.append(f"{prefix} relevant_domain has no cards dir: {domain}")

        for cid in entry.get("recommended_practices", []):
            if cid not in card_ids:
                errors.append(f"{prefix} recommended_practice card_id not found: {cid}")

        brief_rel = entry.get("brief")
        if brief_rel:
            brief_path = PORTFOLIO_ROOT / brief_rel
            if not brief_path.exists():
                errors.append(f"{prefix} brief file not found: {brief_rel}")
            else:
                heading = brief_project_name(brief_path)
                if heading != name:
                    errors.append(
                        f"{prefix} brief heading mismatch: PROJECT_BRIEF says "
                        f"{heading!r} (join would silently fail)"
                    )

        if catalog_titles:
            for book in entry.get("relevant_books", []):
                if book not in catalog_titles:
                    warnings.append(f"{prefix} relevant_book not in catalog: {book}")

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"checked {len(entries)} entries, {len(card_ids)} card_ids known: "
          f"{len(errors)} errors, {len(warnings)} warnings")
    if errors:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
