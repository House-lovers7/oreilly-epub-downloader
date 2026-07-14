"""CLI and JSON contract for the local technical knowledge supply system."""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import click

from .cache import CacheManager
from .distillation import build_domain_pack
from .doctor import run_doctor
from .evaluation import evaluate_pairs
from .indexing import IncrementalIndexer
from .lifecycle import CardLifecycle
from .oreilly_adapter import (
    DEFAULT_MAX_BYTES,
    execute_ingest,
    extract_book_id,
    plan_ingest,
    result_payload,
)
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


@main.command("doctor")
@click.option("--repo", type=click.Path(path_type=Path), default=REPO)
@click.option("--soft-limit", type=click.IntRange(min=1), default=DEFAULT_SOFT_LIMIT)
@click.option("--json", "as_json", is_flag=True, help="Emit structured JSON.")
@click.pass_context
def doctor_command(
    context: click.Context, repo: Path, soft_limit: int, as_json: bool
) -> None:
    """Check index, card provenance, lifecycle state, and cache budget."""
    report = run_doctor(repo, soft_limit_bytes=soft_limit)
    payload = dataclasses.asdict(report)
    if as_json:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        click.echo("ok" if report.ok else "failed")
        for finding in report.findings:
            click.echo(f"- {finding.severity}: {finding.code}: {finding.message}")
    if not report.ok:
        context.exit(1)


@main.command("feedback")
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
@click.option("--card-id", multiple=True, help="Stable card ID; repeat as needed.")
@click.option("--chunk-id", multiple=True, help="Stable chunk ID; repeat as needed.")
@click.option("--accepted", "accepted", flag_value=True, default=None)
@click.option("--rejected", "accepted", flag_value=False)
@click.option("--outcome", help="Safe metadata outcome code, without free-form content.")
@click.option("--duration-ms", type=click.IntRange(min=0))
@click.option("--json", "as_json", is_flag=True)
def feedback_command(
    kb_dir: Path,
    card_id: tuple[str, ...],
    chunk_id: tuple[str, ...],
    accepted: bool | None,
    outcome: str | None,
    duration_ms: int | None,
    as_json: bool,
) -> None:
    """Record whether retrieved evidence was adopted, without raw query text."""
    if accepted is None:
        raise click.UsageError("one of --accepted or --rejected is required")
    if not card_id and not chunk_id:
        raise click.UsageError("at least one --card-id or --chunk-id is required")
    event: dict[str, object] = {
        "event": "feedback",
        "card_ids": list(card_id),
        "chunk_ids": list(chunk_id),
        "accepted": accepted,
        "outcome": outcome or ("applied" if accepted else "rejected"),
    }
    if duration_ms is not None:
        event["duration_ms"] = duration_ms
    try:
        MetadataTelemetry(kb_dir / "telemetry" / "events.jsonl").record(event)
    except (OSError, ValueError) as error:
        raise click.ClickException(str(error)) from error
    payload = {"recorded": True, **event}
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2) if as_json else payload)


@main.command("search")
@click.argument("query")
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
@click.option("--domain")
@click.option("--limit", type=click.IntRange(1, 50), default=5, show_default=True)
@click.option(
    "--source-type", type=click.Choice(["epub", "pdf", "md", "markdown", "txt"])
)
@click.option("--semantic/--no-semantic", default=True, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Emit structured JSON.")
@click.option("--telemetry/--no-telemetry", default=True, show_default=True)
def search_command(
    query: str,
    kb_dir: Path,
    domain: str | None,
    limit: int,
    source_type: str | None,
    semantic: bool,
    as_json: bool,
    telemetry: bool,
) -> None:
    """Search cards first, then FTS, then optional local vectors."""
    vector = LazyVectorSearch(kb_dir) if semantic else None
    result = SearchEngine(kb_dir, vector_search=vector).search(
        query, domain=domain, limit=limit, source_type=source_type
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


@main.group("distill")
def distill_group() -> None:
    """Prepare bounded local material for on-demand card distillation."""


@distill_group.command("pack")
@click.argument("domain")
@click.option("--query", multiple=True, required=True)
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
@click.option("--limit-per-query", type=click.IntRange(min=1), default=40)
@click.option("--max-chunks", type=click.IntRange(min=1), default=120)
@click.option(
    "--source-type", type=click.Choice(["epub", "pdf", "md", "markdown", "txt"])
)
@click.option("--output-dir", type=click.Path(path_type=Path))
@click.option("--json", "as_json", is_flag=True)
def distill_pack(
    domain: str,
    query: tuple[str, ...],
    kb_dir: Path,
    limit_per_query: int,
    max_chunks: int,
    source_type: str | None,
    output_dir: Path | None,
    as_json: bool,
) -> None:
    """Write an atomic source pack only after this explicit command."""
    try:
        result = build_domain_pack(
            kb_dir,
            domain,
            list(query),
            limit_per_query=limit_per_query,
            max_chunks=max_chunks,
            source_type=source_type,
            output_dir=output_dir,
        )
    except (OSError, RuntimeError, ValueError) as error:
        raise click.ClickException(str(error)) from error
    payload = {
        **dataclasses.asdict(result),
        "pack_path": str(result.pack_path),
        "manifest_path": str(result.manifest_path),
    }
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2) if as_json else payload)


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


@main.group("eval")
def eval_group() -> None:
    """Score paired baseline/assisted skill utility observations."""


@eval_group.command("score")
@click.option(
    "--cases", "cases_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True
)
@click.option(
    "--baseline", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True
)
@click.option(
    "--assisted", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True
)
@click.option("--json", "as_json", is_flag=True, help="Emit structured JSON.")
@click.pass_context
def eval_score(
    context: click.Context,
    cases_path: Path,
    baseline: Path,
    assisted: Path,
    as_json: bool,
) -> None:
    """Apply the deterministic utility gates to one aligned eval run."""
    try:
        result = evaluate_pairs(
            _load_json_list(cases_path),
            _load_json_list(baseline),
            _load_json_list(assisted),
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise click.ClickException(str(error)) from error
    payload = dataclasses.asdict(result)
    if as_json:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        click.echo("pass" if result.passed else "fail")
        for failure in result.failures:
            click.echo(f"- {failure}")
    if not result.passed:
        context.exit(1)


@main.group("ingest")
def ingest_group() -> None:
    """Plan or execute one explicitly approved source acquisition."""


@ingest_group.command("oreilly")
@click.argument("book")
@click.option("--cookies", type=click.Path(path_type=Path), required=True)
@click.option("--downloads-dir", type=click.Path(path_type=Path), default=REPO / "downloads")
@click.option("--kb-dir", type=click.Path(path_type=Path), default=DEFAULT_KB)
@click.option("--output", type=click.Path(path_type=Path))
@click.option("--max-bytes", type=click.IntRange(min=1), default=DEFAULT_MAX_BYTES)
@click.option("--execute", is_flag=True, help="Perform the approved network operation.")
@click.option("--approve-book-id", help="Exact ID binding for this one execution.")
@click.option("--json", "as_json", is_flag=True)
def ingest_oreilly(
    book: str,
    cookies: Path,
    downloads_dir: Path,
    kb_dir: Path,
    output: Path | None,
    max_bytes: int,
    execute: bool,
    approve_book_id: str | None,
    as_json: bool,
) -> None:
    """Dry-run by default; download and index one approved O'Reilly book."""
    try:
        plan = plan_ingest(book, cookies, max_bytes=max_bytes)
    except ValueError as error:
        raise click.ClickException(str(error)) from error
    if not execute:
        payload = dataclasses.asdict(plan)
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2) if as_json else payload)
        return
    if approve_book_id != extract_book_id(book):
        raise click.ClickException(
            "approval must be bound to this exact book_id via --approve-book-id"
        )
    try:
        result = execute_ingest(
            book,
            cookies,
            approved_book_id=approve_book_id,
            downloads_dir=downloads_dir,
            kb_dir=kb_dir,
            output=output,
            max_bytes=max_bytes,
        )
    except (PermissionError, ValueError, RuntimeError, OSError) as error:
        raise click.ClickException(str(error)) from error
    payload = result_payload(result)
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2) if as_json else payload)


def _load_json_list(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
        raise ValueError(f"{path} must contain a JSON array of objects")
    return payload
