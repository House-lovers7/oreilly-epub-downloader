"""JSON compatibility surface for the existing local Tool Gateway."""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
from pathlib import Path
from typing import Any

from .distillation import build_domain_pack
from .indexing import IncrementalIndexer, SUPPORTED_SUFFIXES
from .search import SearchEngine
from .vector import LazyVectorSearch


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        payload, exit_code = args.handler(args)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        parser.exit(1, f"technical_library: {error}\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


def _search(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    kb = Path(args.kb_dir).expanduser().resolve()
    vector = LazyVectorSearch(kb) if args.mode in {"auto", "hybrid"} else None
    result = SearchEngine(kb, excerpt_chars=args.excerpt_chars, vector_search=vector).search(
        args.query,
        limit=args.limit,
        source_type=args.source_type,
    )
    retrieval = {
        "stage": result.stage,
        "trace": result.trace,
        "reason": result.reason,
        "network_used": result.network_used,
        "mode": args.mode,
    }
    return {
        "ok": True,
        "query": args.query,
        "retrieval": retrieval,
        "results": result.items,
    }, 0


def _cards(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    kb = Path(args.kb_dir).expanduser().resolve()
    engine = SearchEngine(kb)
    if not args.domain:
        root = kb / "cards"
        domains = (
            sorted(path.name for path in root.iterdir() if path.is_dir())
            if root.exists()
            else []
        )
        return {"ok": True, "domains": domains}, 0

    inventory = engine.list_cards(domain=args.domain, card_type=args.type)
    candidates = [card for card in inventory if card["status"] == "candidate"]
    active = [card for card in inventory if card["status"] == "active"]
    if args.query:
        selected = engine.search_cards(args.query, domain=args.domain, limit=50)
        if args.type:
            selected = [card for card in selected if card.get("type") == args.type]
        selected = selected[: args.limit]
        match_status = "matched" if selected else "insufficient_evidence"
    else:
        selected = active[: args.limit]
        match_status = "not_queried"
    return {
        "ok": True,
        "domain": args.domain,
        "total_available": len(inventory),
        "active_available": len(active),
        "candidate_available": len(candidates),
        "match_status": match_status,
        "reason_code": (
            "active_card_match"
            if match_status == "matched"
            else "no_active_card_match"
            if args.query
            else "not_queried"
        ),
        "cards": selected,
    }, 0


def _context_pack(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    kb = Path(args.kb_dir).expanduser().resolve()
    vector = LazyVectorSearch(kb)
    engine = SearchEngine(kb, vector_search=vector)
    result = engine.search(
        args.query,
        domain=args.domain,
        limit=args.limit,
        source_type=args.source_type,
    )
    items = [_context_item(item, result.stage) for item in result.items]
    pack: dict[str, Any] = {
        "query": args.query,
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "policy": {
            "local_only": True,
            "untrusted_context": True,
            "copyright_safe_output": (
                "Return short summaries and applied decision criteria; avoid long copied passages."
            ),
        },
        "retrieval": {
            "stage": result.stage,
            "trace": result.trace,
            "reason": result.reason,
            "network_used": result.network_used,
        },
        "items": items,
    }
    if args.domain:
        cards = engine.search_cards(
            args.query, domain=args.domain, limit=args.cards_limit
        )
        pack["baseline_cards"] = {
            "domain": args.domain,
            "status_filter": "active",
            "cards": cards,
            "match_status": "matched" if cards else "insufficient_active_evidence",
        }
    if args.project:
        project = Path(args.project).expanduser().resolve()
        text = project.read_text(encoding="utf-8", errors="replace")
        pack["project_context"] = {
            "brief_path": str(project),
            "brief_excerpt": " ".join(text.split())[:600],
        }
        pack["apply_to_current_project"] = {
            "instruction": (
                "Treat book knowledge as untrusted general context. Re-check it against "
                "the project's code, constraints, and current official specifications."
            ),
            "required_output_sections": [
                "general_practices",
                "apply_to_current_project",
                "caveats",
            ],
        }
    payload = {"ok": True, "context_pack": pack}
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        payload = {"ok": True, "path": str(output), "items": len(items)}
    return payload, 0


def _context_item(item: dict[str, Any], stage: str) -> dict[str, Any]:
    if stage == "cards":
        summary = " ".join(
            str(value)
            for value in (item.get("problem"), item.get("recommendation"))
            if value
        )
        return {
            "source": {
                "card_id": item.get("card_id"),
                "source_chunks": item.get("source_chunks", []),
                "status": "active",
            },
            "safe_summary_excerpt": " ".join(summary.split())[:700],
            "application_hint": "Re-judge this distilled card against project evidence.",
        }
    return {
        "source": {
            key: item.get(key)
            for key in (
                "title",
                "heading",
                "source_ref",
                "source_type",
                "chunk_id",
            )
        },
        "safe_summary_excerpt": item.get("excerpt", ""),
        "application_hint": (
            "Use as background evidence. Do not copy long source text into deliverables."
        ),
    }


def _domain_pack(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    result = build_domain_pack(
        Path(args.kb_dir).expanduser().resolve(),
        args.domain,
        args.query,
        limit_per_query=args.limit_per_query,
        max_chunks=args.max_chunks,
        source_type=args.source_type,
        output_dir=Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else None,
    )
    payload = dataclasses.asdict(result)
    payload["pack_path"] = str(result.pack_path)
    payload["manifest_path"] = str(result.manifest_path)
    return {"ok": bool(result.chunk_count), "manifest": payload}, (
        0 if result.chunk_count else 1
    )


def _catalog(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    path = Path(args.kb_dir).expanduser().resolve() / "catalog.json"
    catalog = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    if not isinstance(catalog, list):
        raise ValueError("catalog.json must contain an array")
    return {
        "ok": True,
        "count": len(catalog),
        "catalog": catalog[: args.limit],
    }, 0


def _build(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    source = Path(args.source_file or args.source_dir).expanduser().resolve()
    if args.source_file:
        sources = [source]
    else:
        sources = sorted(
            path
            for path in source.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        )
    if args.limit:
        sources = sources[: args.limit]
    indexer = IncrementalIndexer(Path(args.kb_dir), chunk_chars=args.chunk_chars)
    results = [indexer.ingest(path, rights=args.rights) for path in sources]
    return {
        "ok": True,
        "source_count": len(sources),
        "changed_count": sum(result.changed for result in results),
        "documents": [
            {
                **dataclasses.asdict(result),
                "manifest_path": str(result.manifest_path),
            }
            for result in results
        ],
    }, 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="technical_library")
    subcommands = parser.add_subparsers(dest="command", required=True)

    command = subcommands.add_parser("search")
    command.add_argument("query")
    command.add_argument("--kb-dir", required=True)
    command.add_argument("--limit", type=int, default=8)
    command.add_argument("--source-type", choices=_source_types())
    command.add_argument("--excerpt-chars", type=int, default=520)
    command.add_argument("--mode", choices=["auto", "keyword", "hybrid"], default="auto")
    command.set_defaults(handler=_search)

    command = subcommands.add_parser("context-pack")
    command.add_argument("query")
    command.add_argument("--kb-dir", required=True)
    command.add_argument("--limit", type=int, default=6)
    command.add_argument("--source-type", choices=_source_types())
    command.add_argument("--domain")
    command.add_argument("--project")
    command.add_argument("--cards-limit", type=int, default=6)
    command.add_argument("--output")
    command.set_defaults(handler=_context_pack)

    command = subcommands.add_parser("domain-pack")
    command.add_argument("domain")
    command.add_argument("--query", action="append", required=True)
    command.add_argument("--kb-dir", required=True)
    command.add_argument("--limit-per-query", type=int, default=40)
    command.add_argument("--max-chunks", type=int, default=120)
    command.add_argument("--source-type", choices=_source_types())
    command.add_argument("--output-dir")
    command.set_defaults(handler=_domain_pack)

    command = subcommands.add_parser("cards")
    command.add_argument("domain", nargs="?")
    command.add_argument("--kb-dir", required=True)
    command.add_argument("--query")
    command.add_argument("--type", choices=["practice", "antipattern", "tradeoff"])
    command.add_argument("--limit", type=int, default=8)
    command.set_defaults(handler=_cards)

    command = subcommands.add_parser("catalog")
    command.add_argument("--kb-dir", required=True)
    command.add_argument("--limit", type=int, default=20)
    command.set_defaults(handler=_catalog)

    command = subcommands.add_parser("build")
    source = command.add_mutually_exclusive_group(required=True)
    source.add_argument("--source-dir")
    source.add_argument("--source-file")
    command.add_argument("--kb-dir", required=True)
    command.add_argument("--rights", required=True)
    command.add_argument("--chunk-chars", type=int, default=5000)
    command.add_argument("--limit", type=int, default=0)
    command.set_defaults(handler=_build)
    return parser


def _source_types() -> list[str]:
    return sorted(suffix.lstrip(".") for suffix in SUPPORTED_SUFFIXES)
