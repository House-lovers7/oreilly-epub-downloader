#!/usr/bin/env python3
"""Local technical-library entry point with a legacy engine fallback.

Card retrieval is owned here because an unmatched query must return an honest
empty result.  Other legacy commands continue to delegate during migration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "_technical_library" / "technical_library.py"

CARD_FILES = ("practices.jsonl", "antipatterns.jsonl", "tradeoffs.jsonl")


def _terms(query: str) -> list[str]:
    return [
        term.casefold()
        for term in re.split(r"[^\w\u3040-\u30ff\u3400-\u9fff]+", query)
        if len(term) >= 2
    ]


def _card_score(card: dict, terms: list[str]) -> int:
    searchable = json.dumps(
        {
            key: card.get(key)
            for key in (
                "title",
                "problem",
                "recommendation",
                "pitfalls",
                "when_not_to_apply",
                "keywords",
            )
        },
        ensure_ascii=False,
    ).casefold()
    return sum(1 for term in terms if term in searchable)


def cards_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="technical_library cards")
    parser.add_argument("domain", nargs="?", default=None)
    parser.add_argument("--kb-dir", required=True)
    parser.add_argument("--query")
    parser.add_argument("--type", choices=["practice", "antipattern", "tradeoff"])
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)

    root = Path(args.kb_dir).expanduser().resolve() / "cards"
    if not args.domain:
        domains = sorted(path.name for path in root.iterdir() if path.is_dir()) if root.exists() else []
        print(json.dumps({"ok": True, "domains": domains}, ensure_ascii=False, indent=2))
        return 0

    cards: list[dict] = []
    domain_dir = root / args.domain
    for name in CARD_FILES:
        path = domain_dir / name
        if not path.exists():
            continue
        cards.extend(
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if args.type:
        cards = [card for card in cards if card.get("type") == args.type]

    match_status = "not_queried"
    if args.query:
        terms = _terms(args.query)
        scored = [(_card_score(card, terms), card) for card in cards]
        cards = [card for score, card in sorted(scored, key=lambda item: item[0], reverse=True) if score > 0]
        match_status = "matched" if cards else "insufficient_evidence"

    payload = {
        "ok": True,
        "domain": args.domain,
        "total_available": len(cards) if not args.query else sum(
            1
            for name in CARD_FILES
            for _ in (
                (domain_dir / name).read_text(encoding="utf-8").splitlines()
                if (domain_dir / name).exists()
                else []
            )
            if _.strip()
        ),
        "match_status": match_status,
        "cards": cards[: args.limit],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cards":
        raise SystemExit(cards_main(sys.argv[2:]))
    sys.argv[0] = str(SCRIPT)
    runpy.run_path(str(SCRIPT), run_name="__main__")
