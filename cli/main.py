#!/usr/bin/env python3
"""
VeriGreen AI — Agentic ESG Audit CLI

A Typer-based command-line interface for interacting with the VeriGreen AI
ESG audit platform. Provides commands for running audits, viewing claims,
downloading badges, downloading reports, and checking system health.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Optional

import httpx
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

# ---------------------------------------------------------------------------
# App & Console setup
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="verigreen",
    help="🌿 VeriGreen AI — Agentic ESG Audit CLI",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# Branding colours
SUCCESS = "green"
WARNING = "yellow"
ERROR = "red"
BRAND = "bold green"

BANNER = (
    "[bold green]🌿 VeriGreen AI[/bold green] — "
    "[dim]Agentic ESG Audit Platform[/dim]"
)

DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_OUTPUT = "./output"
POLL_INTERVAL_SECONDS = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _print_banner() -> None:
    """Print the VeriGreen branding banner."""
    console.print()
    console.print(Panel(BANNER, expand=False, border_style="green"))
    console.print()


def _api_url(base: str, path: str) -> str:
    """Build a full API URL from *base* and *path*."""
    return f"{base.rstrip('/')}{path}"


def _handle_http_error(exc: Exception) -> None:
    """Print a user-friendly connection error and exit."""
    console.print(
        f"[{ERROR}]✗ Connection error:[/{ERROR}] {exc}",
    )
    console.print(
        f"[dim]Make sure the VeriGreen API server is running and reachable.[/dim]"
    )
    raise typer.Exit(code=1)


def _ensure_output_dir(output: str) -> Path:
    """Create the output directory if it doesn't exist and return it."""
    p = Path(output)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _score_color(score: float | int) -> str:
    """Return a Rich color name for a credibility score."""
    if score <= 2:
        return ERROR
    if score == 3:
        return WARNING
    return SUCCESS


def _download_file(
    url: str,
    dest: Path,
    *,
    timeout: float = 60.0,
) -> Path:
    """Download a binary file from *url* and save it to *dest*. Returns the path."""
    try:
        with httpx.stream("GET", url, timeout=timeout, follow_redirects=True) as resp:
            resp.raise_for_status()
            # Try to infer filename from Content-Disposition header
            cd = resp.headers.get("content-disposition", "")
            filename = ""
            if "filename=" in cd:
                filename = cd.split("filename=")[-1].strip('" ')
            if not filename:
                # Fallback: derive from URL path
                filename = url.rstrip("/").split("/")[-1]
                if not filename:
                    filename = "download.pdf"
            filepath = dest / filename
            with open(filepath, "wb") as fh:
                for chunk in resp.iter_bytes(chunk_size=8192):
                    fh.write(chunk)
            return filepath
    except httpx.HTTPError as exc:
        _handle_http_error(exc)
        return dest  # unreachable but keeps type checkers happy


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def audit(
    source: str = typer.Argument(
        ...,
        help="Path to a PDF file or a URL to scrape.",
    ),
    company: str = typer.Option(
        ...,
        "--company",
        "-c",
        help="Company name (required).",
    ),
    year: Optional[str] = typer.Option(
        None,
        "--year",
        "-y",
        help="Report year, e.g. '2025-26'.",
    ),
    api_url: str = typer.Option(
        DEFAULT_API_URL,
        "--api-url",
        help="Base URL of the VeriGreen API server.",
    ),
    output: str = typer.Option(
        DEFAULT_OUTPUT,
        "--output",
        "-o",
        help="Directory to save output files.",
    ),
    wait: bool = typer.Option(
        True,
        "--wait/--no-wait",
        help="Poll the API until the audit completes.",
    ),
) -> None:
    """Run a new ESG audit on a PDF file or URL.

    Examples:
        verigreen audit report.pdf --company "Acme Inc" --year 2025-26
        verigreen audit https://example.com/report.pdf --company "Acme Inc"
    """
    _print_banner()

    # Determine source type
    source_path = Path(source)
    is_file = source_path.is_file()

    try:
        if is_file:
            console.print(f"[dim]Uploading file:[/dim] {source_path.name}")
            with open(source_path, "rb") as fh:
                files = {"file": (source_path.name, fh, "application/pdf")}
                data: dict[str, str] = {"company_name": company}
                if year:
                    data["report_year"] = year
                resp = httpx.post(
                    _api_url(api_url, "/audit"),
                    files=files,
                    data=data,
                    timeout=60.0,
                )
        else:
            # Treat source as a URL
            console.print(f"[dim]Submitting URL:[/dim] {source}")
            payload: dict[str, str] = {
                "url": source,
                "company_name": company,
            }
            if year:
                payload["report_year"] = year
            resp = httpx.post(
                _api_url(api_url, "/audit"),
                data=payload,
                timeout=60.0,
            )

        resp.raise_for_status()
        body = resp.json()
    except httpx.HTTPError as exc:
        _handle_http_error(exc)
        return

    audit_id: str = body.get("audit_id", "unknown")
    console.print(f"[{SUCCESS}]✓ Audit submitted:[/{SUCCESS}] [bold]{audit_id}[/bold]")
    console.print(f"[dim]{body.get('message', '')}[/dim]")

    if not wait:
        console.print("[dim]Use --wait to poll until completion.[/dim]")
        return

    # --- Poll until done or error ---
    result: dict = {}
    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Waiting for audit to complete…", total=None)
        while True:
            time.sleep(POLL_INTERVAL_SECONDS)
            try:
                poll_resp = httpx.get(
                    _api_url(api_url, f"/audit/{audit_id}"),
                    timeout=30.0,
                )
                poll_resp.raise_for_status()
                result = poll_resp.json()
            except httpx.HTTPError as exc:
                _handle_http_error(exc)
                return

            status = result.get("status") or result.get("summary", {}).get("status", "")
            if status == "done":
                progress.update(task, description="[green]Audit complete!")
                break
            if status == "error":
                progress.update(task, description="[red]Audit failed!")
                break
            progress.update(
                task,
                description=f"Status: [yellow]{status}[/yellow] — polling…",
            )

    # --- Print summary table ---
    summary = result.get("summary", {})
    status = result.get("status", summary.get("status", "unknown"))

    if status == "error":
        console.print(f"[{ERROR}]✗ Audit failed.[/{ERROR}]")
        console.print(f"[dim]{result.get('error', 'Unknown error')}[/dim]")
        raise typer.Exit(code=1)

    total_claims = summary.get("total_claims", 0)
    flagged = summary.get("flagged", 0)
    overall_score = summary.get("overall_score", 0)
    pillar_scores = summary.get("pillar_scores", {})

    table = Table(
        title="📊 Audit Summary",
        box=box.ROUNDED,
        title_style="bold green",
        border_style="green",
    )
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Claims", str(total_claims))
    table.add_row("Flagged", f"[{WARNING}]{flagged}[/{WARNING}]")

    for pillar, score in pillar_scores.items():
        color = _score_color(score)
        table.add_row(f"  {pillar}", f"[{color}]{score:.1f}[/{color}]")

    overall_color = _score_color(overall_score)
    table.add_row(
        "Overall Score",
        f"[bold {overall_color}]{overall_score:.1f} / 5.0[/bold {overall_color}]",
    )

    console.print(table)

    # --- Auto-download the report PDF ---
    report_url = _api_url(api_url, f"/report/{audit_id}/download")
    out_dir = _ensure_output_dir(output)
    console.print(f"\n[dim]Downloading report PDF…[/dim]")
    filepath = _download_file(report_url, out_dir)
    console.print(f"[{SUCCESS}]✓ Report saved:[/{SUCCESS}] {filepath}")


@app.command()
def claims(
    audit_id: str = typer.Argument(
        ...,
        help="The audit ID to list claims for.",
    ),
    api_url: str = typer.Option(
        DEFAULT_API_URL,
        "--api-url",
        help="Base URL of the VeriGreen API server.",
    ),
    pillar: Optional[str] = typer.Option(
        None,
        "--pillar",
        "-p",
        help="Filter by ESG pillar: Environmental, Social, Governance.",
    ),
    max_score: Optional[int] = typer.Option(
        None,
        "--max-score",
        "-m",
        help="Only show claims with score ≤ this value (1-5).",
    ),
) -> None:
    """List and display ESG claims from a completed audit.

    Examples:
        verigreen claims abc-123
        verigreen claims abc-123 --pillar Environmental --max-score 3
    """
    _print_banner()

    params: dict[str, str | int] = {}
    if pillar:
        params["pillar"] = pillar
    if max_score is not None:
        params["max_score"] = max_score

    try:
        resp = httpx.get(
            _api_url(api_url, f"/claims/{audit_id}"),
            params=params,
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        _handle_http_error(exc)
        return

    if not data:
        console.print(f"[{WARNING}]No claims found for audit {audit_id}.[/{WARNING}]")
        raise typer.Exit()

    claim_list = data if isinstance(data, list) else data.get("claims", data)
    if not isinstance(claim_list, list):
        claim_list = [claim_list]

    table = Table(
        title=f"📋 Claims — Audit [bold]{audit_id}[/bold]",
        box=box.ROUNDED,
        title_style="bold green",
        border_style="green",
        show_lines=True,
    )
    table.add_column("ID", style="dim", width=8)
    table.add_column("Claim", max_width=60)
    table.add_column("Pillar", style="cyan")
    table.add_column("Score", justify="center", width=7)
    table.add_column("Verdict", width=18)

    for claim in claim_list:
        claim_id = str(claim.get("claim_id", claim.get("id", "")))
        text = str(claim.get("text", claim.get("claim_text", "")))
        truncated = (text[:57] + "…") if len(text) > 60 else text
        p = str(claim.get("pillar", ""))
        score = claim.get("final_score") or claim.get("score") or claim.get("credibility_score", 0)
        score_val = int(score) if score else 0
        color = _score_color(score_val)
        verdict = str(claim.get("verdict", ""))

        # Color the verdict
        verdict_colors = {
            "verified": SUCCESS,
            "partially_verified": WARNING,
            "unverified": ERROR,
            "contradicted": ERROR,
        }
        v_color = verdict_colors.get(verdict, "white")

        table.add_row(
            claim_id,
            truncated,
            p,
            f"[{color}]{score_val}[/{color}]",
            f"[{v_color}]{verdict}[/{v_color}]",
        )

    console.print(table)
    console.print(f"[dim]Total: {len(claim_list)} claim(s)[/dim]")


@app.command()
def badge(
    claim_id: str = typer.Argument(
        ...,
        help="The claim ID to download the badge for.",
    ),
    api_url: str = typer.Option(
        DEFAULT_API_URL,
        "--api-url",
        help="Base URL of the VeriGreen API server.",
    ),
    output: str = typer.Option(
        DEFAULT_OUTPUT,
        "--output",
        "-o",
        help="Directory to save the badge PDF.",
    ),
) -> None:
    """Download a trust-badge PDF for a specific claim.

    Examples:
        verigreen badge c001
        verigreen badge c001 --output ./badges
    """
    _print_banner()

    out_dir = _ensure_output_dir(output)
    url = _api_url(api_url, f"/badge/{claim_id}")

    console.print(f"[dim]Downloading badge for claim [bold]{claim_id}[/bold]…[/dim]")
    filepath = _download_file(url, out_dir)
    console.print(f"[{SUCCESS}]✓ Badge saved:[/{SUCCESS}] {filepath}")


@app.command()
def report(
    audit_id: str = typer.Argument(
        ...,
        help="The audit ID to download the report for.",
    ),
    api_url: str = typer.Option(
        DEFAULT_API_URL,
        "--api-url",
        help="Base URL of the VeriGreen API server.",
    ),
    output: str = typer.Option(
        DEFAULT_OUTPUT,
        "--output",
        "-o",
        help="Directory to save the report PDF.",
    ),
) -> None:
    """Download the full audit report PDF.

    Examples:
        verigreen report abc-123
        verigreen report abc-123 --output ./reports
    """
    _print_banner()

    out_dir = _ensure_output_dir(output)
    url = _api_url(api_url, f"/report/{audit_id}/download")

    console.print(
        f"[dim]Downloading report for audit [bold]{audit_id}[/bold]…[/dim]"
    )
    filepath = _download_file(url, out_dir)
    console.print(f"[{SUCCESS}]✓ Report saved:[/{SUCCESS}] {filepath}")


@app.command()
def health(
    api_url: str = typer.Option(
        DEFAULT_API_URL,
        "--api-url",
        help="Base URL of the VeriGreen API server.",
    ),
) -> None:
    """Check the health status of all VeriGreen subsystems.

    Displays color-coded status for: API, Ollama, ChromaDB, SQLite.
    """
    _print_banner()

    try:
        resp = httpx.get(
            _api_url(api_url, "/health"),
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        _handle_http_error(exc)
        return

    # Build a Rich renderable for each subsystem
    subsystems = [
        ("api", "API Server"),
        ("ollama", "Ollama LLM"),
        ("chromadb", "ChromaDB"),
        ("sqlite", "SQLite"),
    ]

    lines: list[str] = []
    for key, label in subsystems:
        status = data.get(key, "unknown")
        if status == "ok":
            indicator = f"[{SUCCESS}]●[/{SUCCESS}]"
            status_text = f"[{SUCCESS}]{status}[/{SUCCESS}]"
        elif status in ("unreachable", "error"):
            indicator = f"[{ERROR}]●[/{ERROR}]"
            status_text = f"[{ERROR}]{status}[/{ERROR}]"
        else:
            indicator = f"[{WARNING}]●[/{WARNING}]"
            status_text = f"[{WARNING}]{status}[/{WARNING}]"
        lines.append(f"  {indicator}  {label:<16} {status_text}")

    # Include Ollama model info if present
    model = data.get("ollama_model")
    if model:
        lines.append(f"\n  [dim]Ollama model:[/dim] {model}")

    panel_text = "\n".join(lines)
    console.print(
        Panel(
            panel_text,
            title="🏥 System Health",
            title_align="left",
            border_style="green",
            expand=False,
        )
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()
