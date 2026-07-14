"""CLI and JSON contract for the local technical knowledge supply system."""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import click

from .cache import CacheManager
from .indexing import IncrementalIndexer
from .lifecycle import CardLifecycle
from .search import SearchEngine
from .telemetry import MetadataTelemetry
from .vector import LazyVectorSearch


REPO = Path(__file__).resolve().parents[1]
DEFAULT_KB = REPO / "knowledge-base"
DEFAULT_SOFT_LIMIT = 5 * 1024 * 1024 * 1024


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="technical-knowledge-supply")
def main() -> None:
    """Local technical knowledge supply system."""


@main.command("search")
@click.argument("query")
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
@click.option("--domain")
@click.option("--limit", type=click.IntRange(1, 50), default=5, show_default=True)
@click.option("--semantic/--no-semantic", default=True, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Emit structured JSON.")
@click.option("--telemetry/--no-telemetry", default=True, show_default=True)
def search_command(
    query: str,
    kb_dir: Path,
    domain: str | None,
    limit: int,
    semantic: bool,
    as_json: bool,
    telemetry: bool,
) -> None:
    """Search cards first, then FTS, then optional local vectors."""
    vector = LazyVectorSearch(kb_dir) if semantic else None
    result = SearchEngine(kb_dir, vector_search=vector).search(
        query, domain=domain, limit=limit
    )
    payload = dataclasses.asdict(result)
    if telemetry:
        card_ids = [item["card_id"] for item in result.items if "card_id" in item]
        chunk_ids = [item["chunk_id"] for item in result.items if "chunk_id" in item]
        MetadataTelemetry(kb_dir / "telemetry" / "events.jsonl").record(
            {
                "event": "search",
                "stage": result.stage,
                "result_count": len(result.items),
                "card_ids": card_ids,
                "chunk_ids": chunk_ids,
                "domain": domain or "all",
                "reason_code": result.reason,
            }
        )
    if as_json:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    click.echo(f"stage: {result.stage} ({result.reason})")
    for item in result.items:
        identifier = item.get("card_id") or item.get("chunk_id") or "item"
        title = item.get("title") or item.get("heading") or ""
        click.echo(f"- {identifier}: {title}")


@main.command("section")
@click.argument("chunk_id")
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
@click.option("--json", "as_json", is_flag=True)
def section_command(chunk_id: str, kb_dir: Path, as_json: bool) -> None:
    """Explicitly read one full section by stable chunk ID."""
    section = SearchEngine(kb_dir).get_section(chunk_id)
    if section is None:
        raise click.ClickException(f"chunk not found: {chunk_id}")
    if as_json:
        click.echo(json.dumps(section, ensure_ascii=False, indent=2))
    else:
        click.echo(section["text"])


@main.group("index")
def index_group() -> None:
    """Incrementally index owned local documents."""


@index_group.command("add")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
@click.option("--rights", required=True, help="Rights classification for this source.")
@click.option("--json", "as_json", is_flag=True)
def index_add(source: Path, kb_dir: Path, rights: str, as_json: bool) -> None:
    """Add or refresh one source without rebuilding unrelated documents."""
    result = IncrementalIndexer(kb_dir).ingest(source, rights=rights)
    payload = {**dataclasses.asdict(result), "manifest_path": str(result.manifest_path)}
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2) if as_json else payload)


@main.group("cards")
def cards_group() -> None:
    """Inspect and transition card lifecycle state."""


@cards_group.command("status")
@click.argument("card_id")
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
def card_status(card_id: str, kb_dir: Path) -> None:
    click.echo(CardLifecycle(kb_dir / "cards" / "lifecycle.json").status(card_id))


@cards_group.command("transition")
@click.argument("card_id")
@click.argument("status", type=click.Choice(["candidate", "active", "deprecated", "archived"]))
@click.option("--basis", required=True)
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
def card_transition(card_id: str, status: str, basis: str, kb_dir: Path) -> None:
    lifecycle = CardLifecycle(kb_dir / "cards" / "lifecycle.json")
    lifecycle.transition(card_id, status, basis=basis)
    click.echo(f"{card_id}: {status}")


@main.group("cache")
def cache_group() -> None:
    """Report cache budget and produce non-destructive prune plans."""


@cache_group.command("status")
@click.option("--repo", type=click.Path(path_type=Path), default=REPO)
@click.option("--soft-limit", type=int, default=DEFAULT_SOFT_LIMIT)
def cache_status(repo: Path, soft_limit: int) -> None:
    payload = dataclasses.asdict(CacheManager(repo, soft_limit_bytes=soft_limit).status())
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@cache_group.command("prune-plan")
@click.option("--repo", type=click.Path(path_type=Path), default=REPO)
@click.option("--target-bytes", required=True, type=click.IntRange(min=1))
@click.option("--soft-limit", type=int, default=DEFAULT_SOFT_LIMIT)
def cache_prune_plan(repo: Path, target_bytes: int, soft_limit: int) -> None:
    manager = CacheManager(repo, soft_limit_bytes=soft_limit)
    click.echo(
        json.dumps(
            {"dry_run": True, "candidates": [str(path) for path in manager.prune_plan(target_bytes=target_bytes)]},
            ensure_ascii=False,
            indent=2,
        )
    )
