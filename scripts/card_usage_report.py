#!/usr/bin/env python3
"""Report which knowledge-base cards are actually used in review artifacts.

Scans text files for card_id references (e.g. sec-p-004) and aggregates:
  - used cards: occurrence count + referencing files, grouped by domain
  - unused (dormant) cards: never referenced anywhere scanned
  - FTS fallback queries: lines marked `FTS-fallback:` (engineer-brain 等が
    カード不在で全文検索へ落ちた需要の記録。未計装ならその旨を表示)

Default scan roots:
  knowledge-base/reports/            (pilot / design reviews)
  ../                                project_map.jsonl recommended_practices は
                                     「割当」であり「使用」ではないため対象外
  /Users/tg/projects/agent-company-os/logs/   (decision log / lessons)

Usage:
  python3 scripts/card_usage_report.py [--scan-dir DIR ...] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CARDS = REPO / "knowledge-base" / "cards"
DEFAULT_SCAN_DIRS = [
    REPO / "knowledge-base" / "reports",
    Path("/Users/tg/projects/agent-company-os/logs"),
]
CARD_FILES = ("practices.jsonl", "antipatterns.jsonl", "tradeoffs.jsonl")
CARD_ID_RE = re.compile(r"\b(?:arch|sre|sec|db|api|net|perf|test|dp)-[pat]-\d{3}\b")
FALLBACK_RE = re.compile(r"FTS-fallback:\s*(.+)")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".log"}
# 割当ファイル自身と蒸留素材は「使用」実績に数えない（割当≠使用）
EXCLUDE_NAMES = {"project_map.jsonl", "source-pack.jsonl"}
EXCLUDE_PREFIXES = ("project-map-expansion",)


def load_cards() -> dict[str, dict]:
    cards: dict[str, dict] = {}
    for domain_dir in sorted(CARDS.iterdir()):
        if not domain_dir.is_dir():
            continue
        for name in CARD_FILES:
            f = domain_dir / name
            if not f.exists():
                continue
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    c = json.loads(line)
                    cards[c["card_id"]] = {"domain": c["domain"], "type": c["type"], "title": c["title"]}
    return cards


def iter_scan_files(scan_dirs: list[Path]):
    for root in scan_dirs:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if (p.is_file() and p.suffix in TEXT_SUFFIXES and p.name not in EXCLUDE_NAMES
                    and not p.name.startswith(EXCLUDE_PREFIXES)):
                yield p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scan-dir", action="append", type=Path, default=None,
                    help="追加/置換のスキャン対象ディレクトリ（複数指定可。省略時は既定2箇所）")
    ap.add_argument("--json", action="store_true", help="機械可読JSONで出力")
    args = ap.parse_args()

    scan_dirs = args.scan_dir if args.scan_dir else DEFAULT_SCAN_DIRS
    cards = load_cards()
    if not cards:
        print("ERROR: no cards found under", CARDS)
        return 1

    used: dict[str, dict] = defaultdict(lambda: {"count": 0, "files": set()})
    unknown_ids: dict[str, set] = defaultdict(set)
    fallback_queries: list[dict] = []
    scanned = 0

    for f in iter_scan_files(scan_dirs):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        rel = str(f)
        for cid in CARD_ID_RE.findall(text):
            if cid in cards:
                used[cid]["count"] += 1
                used[cid]["files"].add(rel)
            else:
                unknown_ids[cid].add(rel)
        for m in FALLBACK_RE.finditer(text):
            fallback_queries.append({"query": m.group(1).strip(), "file": rel})

    unused = sorted(set(cards) - set(used))
    by_domain_used: dict[str, int] = defaultdict(int)
    by_domain_total: dict[str, int] = defaultdict(int)
    for cid, meta in cards.items():
        by_domain_total[meta["domain"]] += 1
        if cid in used:
            by_domain_used[meta["domain"]] += 1

    if args.json:
        print(json.dumps({
            "scanned_files": scanned,
            "scan_dirs": [str(d) for d in scan_dirs],
            "used": {cid: {"count": v["count"], "files": sorted(v["files"]),
                           **cards[cid]} for cid, v in sorted(used.items())},
            "unused_count": len(unused),
            "unused": unused,
            "unknown_card_ids": {k: sorted(v) for k, v in sorted(unknown_ids.items())},
            "domain_coverage": {d: {"used": by_domain_used[d], "total": by_domain_total[d]}
                                for d in sorted(by_domain_total)},
            "fts_fallback_queries": fallback_queries,
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"scanned {scanned} files under: " + ", ".join(str(d) for d in scan_dirs))
    print()
    print("## 使用されたカード（レビュー成果物での引用）")
    if used:
        for cid, v in sorted(used.items(), key=lambda kv: -kv[1]["count"]):
            m = cards[cid]
            print(f"  {cid}  x{v['count']:<3} [{m['domain']}/{m['type']}] {m['title']}")
            for fp in sorted(v["files"]):
                print(f"      - {fp}")
    else:
        print("  (なし)")
    print()
    print("## ドメイン別カバレッジ（使用/総数）")
    for d in sorted(by_domain_total):
        print(f"  {d:<14} {by_domain_used[d]:>3} / {by_domain_total[d]}")
    print()
    print(f"## 死蔵カード: {len(unused)} / {len(cards)}")
    print("  （--json で全IDを出力。死蔵が多いドメインは蒸留過剰か結線不足のシグナル）")
    if unknown_ids:
        print()
        print("## 実在しない card_id の引用（要修正）")
        for cid, files in sorted(unknown_ids.items()):
            print(f"  {cid}: " + ", ".join(sorted(files)))
    print()
    print("## FTSフォールバック需要（カード不在で全文検索に落ちたクエリ）")
    if fallback_queries:
        for q in fallback_queries:
            print(f"  - {q['query']}  ({q['file']})")
    else:
        print("  記録なし。engineer-brain / book-knowledge-pack 側が `FTS-fallback: <query>` 形式で")
        print("  決定ログ・lessonsに残せば、ここに集計され次の蒸留対象ドメインの根拠になる（現状は未計装）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
