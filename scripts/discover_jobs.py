#!/usr/bin/env python3
"""
Job Discovery Script — Agent 0
Hunts scraping jobs from Upwork RSS, Freelancer API, and search engines.
Saves qualified raw listings to queue/raw_jobs.json
"""

import json
import feedparser
import requests
import hashlib
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()
QUEUE_FILE = Path(__file__).parent.parent / "queue" / "raw_jobs.json"
SEEN_FILE  = Path(__file__).parent.parent / "queue" / "seen_ids.json"

# ─── SEARCH QUERIES ──────────────────────────────────────────────────────────

UPWORK_QUERIES = [
    "web scraping",
    "python scraper",
    "data extraction csv",
    "beautifulsoup",
    "playwright scraping",
    "scrapy spider",
    "crawl website data",
]

FREELANCER_QUERIES = [
    "web scraping",
    "python beautifulsoup",
    "data extraction",
    "csv scraper",
]

# ─── UPWORK RSS FEED ─────────────────────────────────────────────────────────

def fetch_upwork_rss(query: str) -> list[dict]:
    """Upwork has public RSS feeds — no auth required."""
    url = (
        "https://www.upwork.com/ab/feed/jobs/rss"
        f"?q={requests.utils.quote(query)}"
        "&sort=recency"
        "&budget=50-"          # min $50
        "&job_type=fixed"
    )
    headers = {"User-Agent": "Mozilla/5.0 (compatible; feedfetcher)"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        feed = feedparser.parse(resp.text)
        jobs = []
        for entry in feed.entries:
            jobs.append({
                "source": "upwork",
                "id": hashlib.md5(entry.get("link","").encode()).hexdigest()[:12],
                "title": entry.get("title", ""),
                "description": entry.get("summary", "")[:1200],
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "query_used": query,
                "fetched_at": datetime.utcnow().isoformat(),
            })
        return jobs
    except Exception as e:
        console.print(f"[yellow]Upwork RSS error ({query}): {e}[/yellow]")
        return []


# ─── FREELANCER API ───────────────────────────────────────────────────────────

def fetch_freelancer_api(query: str) -> list[dict]:
    """Freelancer public search API — no auth for basic listing search."""
    url = "https://www.freelancer.com/api/projects/0.1/projects/active/"
    params = {
        "query": query,
        "job_details": "true",
        "limit": 20,
        "offset": 0,
        "sort_field": "time_updated",
        "min_avg_price": 20,
        "project_types[]": "fixed",
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "freelancer-client": "freelancer-sdk-js",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        data = resp.json()
        jobs = []
        for p in data.get("result", {}).get("projects", []):
            jobs.append({
                "source": "freelancer",
                "id": f"fl_{p.get('id','')}",
                "title": p.get("title", ""),
                "description": p.get("description", "")[:1200],
                "url": f"https://www.freelancer.com/projects/{p.get('seo_url','')}",
                "budget_min": p.get("budget", {}).get("minimum", 0),
                "budget_max": p.get("budget", {}).get("maximum", 0),
                "published": p.get("time_updated", ""),
                "query_used": query,
                "fetched_at": datetime.utcnow().isoformat(),
            })
        return jobs
    except Exception as e:
        console.print(f"[yellow]Freelancer API error ({query}): {e}[/yellow]")
        return []


# ─── DEDUPLICATION ────────────────────────────────────────────────────────────

def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()

def save_seen(seen: set):
    SEEN_FILE.write_text(json.dumps(list(seen)))

def load_queue() -> list:
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []

def save_queue(jobs: list):
    QUEUE_FILE.write_text(json.dumps(jobs, indent=2))


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def run_discovery():
    console.print("[bold cyan]🔍 Agent 0 — Job Discovery Starting...[/bold cyan]")
    seen = load_seen()
    existing = load_queue()
    new_jobs = []

    # Upwork RSS
    console.print("\n[bold]Scanning Upwork RSS...[/bold]")
    for q in UPWORK_QUERIES:
        jobs = fetch_upwork_rss(q)
        for j in jobs:
            if j["id"] not in seen:
                seen.add(j["id"])
                new_jobs.append(j)
        console.print(f"  [{q}] → {len(jobs)} found")

    # Freelancer
    console.print("\n[bold]Scanning Freelancer API...[/bold]")
    for q in FREELANCER_QUERIES:
        jobs = fetch_freelancer_api(q)
        for j in jobs:
            if j["id"] not in seen:
                seen.add(j["id"])
                new_jobs.append(j)
        console.print(f"  [{q}] → {len(jobs)} found")

    # Merge into queue
    all_jobs = existing + new_jobs
    save_queue(all_jobs)
    save_seen(seen)

    # Summary table
    table = Table(title=f"Discovery Results — {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")
    table.add_column("Source")
    table.add_column("New Jobs")
    table.add_column("Queue Total")

    upwork_new  = sum(1 for j in new_jobs if j["source"] == "upwork")
    fl_new      = sum(1 for j in new_jobs if j["source"] == "freelancer")

    table.add_row("Upwork",     str(upwork_new),  "—")
    table.add_row("Freelancer", str(fl_new),       "—")
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{len(new_jobs)}[/bold]", f"[bold]{len(all_jobs)}[/bold]")
    console.print(table)
    console.print(f"\n✓ Queue saved to: {QUEUE_FILE}")

if __name__ == "__main__":
    run_discovery()
