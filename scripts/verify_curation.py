#!/usr/bin/env python3
"""curation/*.tsv の実例文がsentences.jsonlに逐語実在するかを全数検証する。

使い方: python3 scripts/verify_curation.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "knowledge-base" / "english-corpus" / "data"
CURATION_DIR = ROOT / "knowledge-base" / "english-corpus" / "curation"

EXPECTED_HEADER = [
    "expression",
    "pos",
    "gloss_ja",
    "nuance",
    "example_sentence",
    "source_book",
]


def load_sentences() -> dict[str, list[tuple[str, str]]]:
    index: dict[str, list[tuple[str, str]]] = {}
    with (DATA_DIR / "sentences.jsonl").open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            key = row["key"]
            pairs = [(s["text"], s["book"]) for s in row["sentences"]]
            index[key] = pairs
    return index


def verify_file(path: Path, sentence_index: dict[str, list[tuple[str, str]]]) -> dict:
    report = {
        "file": path.name,
        "rows": 0,
        "header_ok": False,
        "field_count_errors": [],
        "missing_key_errors": [],
        "quote_mismatch_errors": [],
        "empty_field_errors": [],
        "duplicate_expressions": [],
        "katakana_flagged": [],
    }
    if not path.exists():
        report["fatal"] = "file not found"
        return report

    seen_expr: set[str] = set()
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        try:
            header = next(reader)
        except StopIteration:
            report["fatal"] = "empty file"
            return report
        report["header_ok"] = header == EXPECTED_HEADER
        if not report["header_ok"]:
            report["header_actual"] = header

        for lineno, row in enumerate(reader, start=2):
            if not row:
                continue
            report["rows"] += 1
            if len(row) != 6:
                report["field_count_errors"].append((lineno, len(row), row[:1]))
                continue
            expr, pos, gloss, nuance, example, book = row

            for fname, val in [
                ("expression", expr),
                ("pos", pos),
                ("gloss_ja", gloss),
                ("nuance", nuance),
                ("example_sentence", example),
                ("source_book", book),
            ]:
                if not val.strip():
                    report["empty_field_errors"].append((lineno, fname))

            if expr in seen_expr:
                report["duplicate_expressions"].append((lineno, expr))
            seen_expr.add(expr)

            key = expr.strip().lower()
            pairs = sentence_index.get(key)
            if pairs is None:
                report["missing_key_errors"].append((lineno, expr))
                continue
            if (example, book) not in pairs:
                report["quote_mismatch_errors"].append((lineno, expr, example[:60]))

    return report


def print_report(r: dict) -> bool:
    ok = True
    print(f"\n=== {r['file']} ===")
    if r.get("fatal"):
        print(f"  FATAL: {r['fatal']}")
        return False
    print(f"  rows: {r['rows']}")
    if not r["header_ok"]:
        ok = False
        print(f"  [FAIL] header mismatch: {r.get('header_actual')}")
    for key, label in [
        ("field_count_errors", "field count != 6"),
        ("missing_key_errors", "expression not a sentences.jsonl key"),
        ("quote_mismatch_errors", "(example, book) not verbatim in sentences.jsonl"),
        ("empty_field_errors", "empty required field"),
        ("duplicate_expressions", "duplicate expression within file"),
    ]:
        errs = r[key]
        if errs:
            ok = False
            print(f"  [FAIL] {label}: {len(errs)}")
            for e in errs[:10]:
                print(f"    {e}")
            if len(errs) > 10:
                print(f"    ... and {len(errs) - 10} more")
        else:
            print(f"  [OK] {label}: 0")
    row_range_ok = 95 <= r["rows"] <= 120
    print(f"  row count in [95,120]: {'OK' if row_range_ok else 'NOTE (may be intentional for discourse/speaking)'}")
    return ok


def main() -> int:
    sentence_index = load_sentences()
    files = sorted(CURATION_DIR.glob("*.tsv"))
    if not files:
        print(f"No .tsv files found in {CURATION_DIR}")
        return 1

    all_ok = True
    all_expressions: dict[str, list[str]] = {}
    for path in files:
        r = verify_file(path, sentence_index)
        ok = print_report(r)
        all_ok = all_ok and ok

    # cross-file duplicate check
    print("\n=== cross-file duplicate expressions ===")
    seen: dict[str, str] = {}
    dupes = []
    for path in files:
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            next(reader, None)
            for row in reader:
                if not row:
                    continue
                expr = row[0].strip().lower()
                if expr in seen and seen[expr] != path.name:
                    dupes.append((expr, seen[expr], path.name))
                else:
                    seen[expr] = path.name
    if dupes:
        print(f"  [NOTE] {len(dupes)} cross-file duplicates (dedup at integration stage):")
        for d in dupes[:20]:
            print(f"    {d}")
    else:
        print("  [OK] no cross-file duplicates")

    print(f"\n=== overall: {'PASS' if all_ok else 'FAIL'} ===")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
