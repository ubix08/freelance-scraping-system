#!/usr/bin/env python3
"""
Pipeline Runner — Master Orchestrator
Runs the full discovery → qualify → analyze loop.

Usage:
  python run_pipeline.py discover     # Agent 0: hunt new jobs
  python run_pipeline.py qualify      # Agent 1: filter queue
  python run_pipeline.py analyze      # Agent 4: analyze top jobs' target sites
  python run_pipeline.py full         # Run all three in sequence
  python run_pipeline.py show         # Show current qualified jobs
"""

import sys
import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
BASE    = Path(__file__).parent.parent
SCRIPTS = Path(__file__).parent


def run_script(name: str):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / name)],
        cwd=str(BASE),
    )
    return result.returncode == 0


def show_qualified():
    qfile = BASE / "queue" / "qualified_jobs.json"
    if not qfile.exists():
        console.print("[yellow]No qualified jobs yet. Run: python run_pipeline.py qualify[/yellow]")
        return

    jobs = json.loads(qfile.read_text())
    if not jobs:
        console.print("[yellow]Queue is empty.[/yellow]")
        return

    table = Table(title=f"Qualified Jobs ({len(jobs)} total)", show_lines=True)
    table.add_column("#",          width=4)
    table.add_column("Source",     width=12)
    table.add_column("Title",      width=45)
    table.add_column("Decision",   width=8)
    table.add_column("Complexity", width=10)
    table.add_column("Price",      width=8)
    table.add_column("URL",        width=40)

    for i, j in enumerate(jobs[:20], 1):
        q = j.get("qualification", {})
        dec = q.get("decision", "?")
        color = "green" if dec == "ACCEPT" else "yellow"
        table.add_row(
            str(i),
            j.get("source", ""),
            j.get("title","")[:45],
            f"[{color}]{dec}[/{color}]",
            q.get("complexity","?"),
            q.get("suggested_price","?"),
            j.get("url","")[:40],
        )

    console.print(table)
    console.print(f"\n[dim]Showing top 20 of {len(jobs)}. Full list: queue/qualified_jobs.json[/dim]")


def analyze_top(n: int = 3):
    """Run site analysis on the top N accepted jobs."""
    qfile = BASE / "queue" / "qualified_jobs.json"
    if not qfile.exists():
        console.print("[red]No qualified jobs. Run qualify first.[/red]")
        return

    jobs = json.loads(qfile.read_text())
    accepted = [j for j in jobs if j.get("qualification",{}).get("decision") == "ACCEPT"][:n]

    if not accepted:
        console.print("[yellow]No accepted jobs to analyze.[/yellow]")
        return

    console.print(f"\n[bold]Running site analysis on top {len(accepted)} jobs...[/bold]")
    for job in accepted:
        # Extract URL from description if we have a target site
        url = job.get("url","")
        console.print(f"\n  Job: {job['title'][:60]}")
        console.print(f"  Source: {url}")
        console.print(f"  [dim]Note: Ask client for target site URL, then run:[/dim]")
        console.print(f"  [cyan]python scripts/analyze_site.py <target_site_url>[/cyan]")


COMMANDS = {
    "discover": lambda: run_script("discover_jobs.py"),
    "qualify":  lambda: run_script("process_queue.py"),
    "analyze":  lambda: analyze_top(3),
    "show":     lambda: show_qualified(),
    "full": lambda: (
        console.print(Panel("[bold cyan]Running Full Pipeline[/bold cyan]")),
        run_script("discover_jobs.py") and
        run_script("process_queue.py") and
        show_qualified()
    ),
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd not in COMMANDS:
        console.print(f"[red]Unknown command: {cmd}[/red]")
        console.print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)
    COMMANDS[cmd]()
