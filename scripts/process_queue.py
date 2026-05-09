#!/usr/bin/env python3
"""
Queue Processor — Agent 1 Automation Layer
Reads raw_jobs.json, applies qualification rules, outputs qualified_jobs.json
"""

import json
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()
QUEUE_FILE     = Path(__file__).parent.parent / "queue" / "raw_jobs.json"
QUALIFIED_FILE = Path(__file__).parent.parent / "queue" / "qualified_jobs.json"
REJECTED_FILE  = Path(__file__).parent.parent / "queue" / "rejected_jobs.json"

# ─── SCORING RULES ────────────────────────────────────────────────────────────

ACCEPT_KEYWORDS = [
    "scraping", "scraper", "beautifulsoup", "playwright", "scrapy",
    "selenium", "crawl", "crawling", "data extraction", "extract data",
    "csv", "excel", "spreadsheet", "dataset", "parse", "parsing",
    "python script", "web data", "product data", "price data",
    "lead list", "contact list", "directory",
]

REJECT_KEYWORDS = [
    "salesforce", "hubspot", "crm integration", "n8n", "zapier", "make.com",
    "google sheets api", "airtable", "ongoing", "long-term contract",
    "monthly retainer", "part-time", "full-time", "wordpress plugin",
    "browser extension", "mobile app", "ios", "android",
]

COMPLEXITY_SIGNALS = {
    "low": [
        "simple", "basic", "static site", "html", "product list",
        "csv output", "one-time", "small dataset", "under 1000",
        "500 rows", "100 items",
    ],
    "medium": [
        "pagination", "multiple pages", "login required", "authenticated",
        "javascript", "dynamic", "react", "vue", "angular",
        "10000", "large dataset",
    ],
    "high": [
        "captcha", "cloudflare", "anti-bot", "protected", "bypass",
        "millions", "real-time", "api integration", "scheduled",
        "ongoing scraping", "cron", "database",
    ],
}


def extract_budget(text: str) -> tuple[float, float]:
    """Extract min/max budget from text."""
    patterns = [
        r'\$(\d+)\s*[-–]\s*\$(\d+)',
        r'\$(\d+)\s*to\s*\$(\d+)',
        r'budget[:\s]+\$(\d+)',
        r'\$(\d+)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            groups = m.groups()
            if len(groups) == 2:
                return float(groups[0]), float(groups[1])
            return float(groups[0]), float(groups[0])
    return 0.0, 0.0


def classify(job: dict) -> dict:
    text = (job.get("title","") + " " + job.get("description","")).lower()

    # Check reject conditions
    for kw in REJECT_KEYWORDS:
        if kw in text:
            return {"decision": "REJECT", "reason": f"contains '{kw}'"}

    # Must have at least one accept keyword
    matched = [kw for kw in ACCEPT_KEYWORDS if kw in text]
    if not matched:
        return {"decision": "REJECT", "reason": "no scraping-related keywords found"}

    # Budget check
    bmin, bmax = extract_budget(job.get("description","") + job.get("title",""))
    job_budget_min = job.get("budget_min", bmin)
    if job_budget_min and float(job_budget_min) < 15:
        return {"decision": "REJECT", "reason": f"budget too low (${job_budget_min})"}

    # Complexity scoring
    complexity = "low"
    for level in ["high", "medium", "low"]:
        if any(sig in text for sig in COMPLEXITY_SIGNALS[level]):
            complexity = level
            break

    # Hold conditions
    hold_signals = ["captcha", "cloudflare", "login", "authenticated", "bypass"]
    if any(s in text for s in hold_signals):
        return {
            "decision": "HOLD",
            "reason": "requires manual review — anti-bot or auth detected",
            "complexity": complexity,
            "matched_keywords": matched[:5],
        }

    return {
        "decision": "ACCEPT",
        "complexity": complexity,
        "matched_keywords": matched[:5],
        "estimated_hours": {"low": 3, "medium": 8, "high": 16}[complexity],
        "suggested_price": {"low": "$75", "medium": "$150", "high": "$250"}[complexity],
    }


def process_queue():
    if not QUEUE_FILE.exists():
        console.print("[red]No queue file found. Run discover_jobs.py first.[/red]")
        return

    raw = json.loads(QUEUE_FILE.read_text())
    accepted, rejected, held = [], [], []

    for job in raw:
        result = classify(job)
        job["qualification"] = result
        if result["decision"] == "ACCEPT":
            accepted.append(job)
        elif result["decision"] == "HOLD":
            held.append(job)
        else:
            rejected.append(job)

    # Save
    QUALIFIED_FILE.write_text(json.dumps(accepted + held, indent=2))
    REJECTED_FILE.write_text(json.dumps(rejected, indent=2))

    # Summary
    table = Table(title="Queue Processing Results")
    table.add_column("Decision", style="bold")
    table.add_column("Count")
    table.add_column("Action")

    table.add_row("[green]ACCEPT[/green]",  str(len(accepted)), "→ qualified_jobs.json")
    table.add_row("[yellow]HOLD[/yellow]",  str(len(held)),     "→ qualified_jobs.json (flagged)")
    table.add_row("[red]REJECT[/red]",      str(len(rejected)), "→ rejected_jobs.json")
    console.print(table)

    # Show top accepted jobs
    if accepted:
        console.print("\n[bold green]Top ACCEPTED Jobs:[/bold green]")
        for j in accepted[:5]:
            q = j["qualification"]
            console.print(
                f"  [{j['source'].upper()}] {j['title'][:70]}"
                f" | {q['complexity']} | {q['suggested_price']} | {j.get('url','')[:60]}"
            )

    console.print(f"\n✓ Qualified jobs saved to: {QUALIFIED_FILE}")


if __name__ == "__main__":
    process_queue()
