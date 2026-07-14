"""Compatibility CLI for the approval-gated O'Reilly input adapter."""

import dataclasses
import json
import sys
from pathlib import Path

import click
from rich.console import Console

from techlib.oreilly_adapter import (
    DEFAULT_MAX_BYTES,
    execute_ingest,
    extract_book_id as _extract_book_id,
    plan_ingest,
    result_payload,
)

console = Console()


def extract_book_id(book_input: str) -> str:
    """Preserve the legacy import while using the strict adapter parser."""
    return _extract_book_id(book_input)


@click.command()
@click.argument("book", required=True)
@click.option(
    "-c",
    "--cookies",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to cookies.json file",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output path (defaults to ./downloads/<title>.epub)",
)
@click.option(
    "--downloads-dir",
    type=click.Path(path_type=Path),
    default=Path("downloads"),
    show_default=True,
)
@click.option(
    "--kb-dir",
    type=click.Path(path_type=Path),
    default=Path("knowledge-base"),
    show_default=True,
)
@click.option("--max-bytes", type=click.IntRange(min=1), default=DEFAULT_MAX_BYTES)
@click.option("--execute", is_flag=True, help="Perform the approved network operation.")
@click.option("--approve-book-id", help="Exact ID binding for this one execution.")
@click.option("--json", "as_json", is_flag=True, help="Emit structured JSON.")
def main(
    book: str,
    cookies: Path,
    output: Path | None,
    downloads_dir: Path,
    kb_dir: Path,
    max_bytes: int,
    execute: bool,
    approve_book_id: str | None,
    as_json: bool,
) -> None:
    """Plan one O'Reilly EPUB ingestion; execution requires explicit approval.

    BOOK can be a book ID or full O'Reilly URL.

    \b
    Examples:
        oreilly-dl 9781098166298 -c cookies.json
        oreilly-dl 9781098166298 -c cookies.json --execute \
          --approve-book-id 9781098166298
    """
    try:
        plan = plan_ingest(book, cookies, max_bytes=max_bytes)
        if not execute:
            payload = dataclasses.asdict(plan)
        else:
            if approve_book_id != plan.book_id:
                raise PermissionError(
                    "approval must be bound to this exact book_id via --approve-book-id"
                )
            payload = result_payload(
                execute_ingest(
                    book,
                    cookies,
                    approved_book_id=approve_book_id,
                    downloads_dir=downloads_dir,
                    kb_dir=kb_dir,
                    output=output,
                    max_bytes=max_bytes,
                )
            )
        if as_json:
            click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        elif not execute:
            console.print("[bold yellow]Dry run:[/] no network request was made")
            console.print(payload)
        else:
            console.print(f"\n[bold green]Done:[/] {payload['output_path']}")
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/]")
        sys.exit(130)
    except (PermissionError, ValueError, RuntimeError, OSError) as error:
        raise click.ClickException(str(error)) from error


if __name__ == "__main__":
    main()
