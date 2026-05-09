#!/usr/bin/env python3
"""
Layer 1 — Market Research Intelligence (automated).
Collects scraping jobs from Upwork RSS, pre-filters, deduplicates with TTL.
Zero LLM cost. Output: queue/collected.json
"""

import json
import os
import re
import time
import feedparser
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_DIR = BASE_DIR / "queue"
LOG_DIR = BASE_DIR / "logs"
DEDUP_TTL_DAYS = 30

# RSS: multiple search term variations
RSS_FEEDS = [
    f"https://www.upwork.com/ab/feed/jobs/rss?q={q}&sort=recency"
    for q in [
        "web+scraping+OR+data+extraction+OR+beautifulsoup",
        "scrape+OR+crawl+OR+scrapy+OR+playwright",
        "python+scraper+OR+data+mining+OR+extract+data",
        "scrape+website+OR+collect+data+OR+harvest+data",
    ]
]

# Preliminary reject keywords (Layer 1 is coarse filter — Layer 2 does fine analysis)
REJECT_IF_CONTAINS = [
    "data entry", "copy paste", "virtual assistant",
    "social media manager", "content writer", "video editor",
    "logo design", "graphic design", "voice over",
    "blockchain", "crypto", "nft",
]

# Keywords that signal it IS a scraping job (for preliminary inclusion)
SCRAPING_SIGNALS = [
    "scrap", "crawl", "extract", "harvest", "collect",
    "beautifulsoup", "scrapy", "playwright", "selenium",
    "python", "data", "csv", "excel", "json", "parse",
    "html", "table", "pric", "listing", "product",
]


def load_json(path):
    if path.exists():
        with open(path) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def preliminary_filter(title, description):
    combined = f"{title} {description}".lower()
    for kw in REJECT_IF_CONTAINS:
        if kw in combined:
            return False
    signal_count = sum(1 for s in SCRAPING_SIGNALS if s in combined)
    return signal_count >= 1


def has_budget_indication(text):
    patterns = [r"\$\s*(\d{2,4})", r"budget", r"fixed.?price", r"hourly"]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def parse_rss(url):
    jobs = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", "").strip()
            published = entry.get("published", "")
            if not preliminary_filter(title, summary):
                continue
            jobs.append({
                "title": title,
                "url": link,
                "description": summary[:2000],
                "source": "upwork_rss",
                "posted": published,
                "has_budget": has_budget_indication(f"{title} {summary}"),
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            })
    except Exception as e:
        print(f"  RSS error: {e}")
    return jobs


def dedup_with_ttl(new_jobs, seen_path):
    """Deduplicate with TTL. Purge entries older than DEDUP_TTL_DAYS."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=DEDUP_TTL_DAYS)

    seen = load_json(seen_path)
    # Purge expired
    seen = [s for s in seen if s.get("timestamp") and datetime.fromisoformat(s["timestamp"]) > cutoff]
    seen_urls = {s["url"] for s in seen}

    fresh = []
    for job in seen:
        fresh.append(job)

    added = 0
    for job in new_jobs:
        url = job.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            fresh.append({"url": url, "timestamp": now.isoformat()})
            added += 1

    save_json(seen_path, fresh)
    return added


def main():
    os.makedirs(QUEUE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    start = datetime.now(timezone.utc)

    print("[LAYER 1] Market Research — collecting scraping jobs...")
    all_jobs = []
    for url in RSS_FEEDS:
        jobs = parse_rss(url)
        all_jobs.extend(jobs)
        time.sleep(0.5)

    # Deduplicate among RSS results (same URL across different queries)
    seen_urls = set()
    unique = []
    for j in all_jobs:
        u = j.get("url", "")
        if u and u not in seen_urls:
            seen_urls.add(u)
            unique.append(j)

    # Deduplicate against history with TTL
    new_added = dedup_with_ttl(unique, QUEUE_DIR / "seen_ids.json")

    # Load existing collected jobs and append new ones
    collected = load_json(QUEUE_DIR / "collected.json")
    existing_urls = {j.get("url", "") for j in collected}
    for j in unique:
        if j.get("url", "") not in existing_urls:
            collected.append(j)

    save_json(QUEUE_DIR / "collected.json", collected)

    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    summary = (
        f"Raw RSS: {len(all_jobs)} | Unique: {len(unique)} | "
        f"New: {new_added} | Total collected: {len(collected)} | "
        f"Time: {elapsed:.1f}s"
    )
    print(f"\n[LAYER 1] {summary}")

    with open(LOG_DIR / "market_research.log", "a") as f:
        f.write(f"{datetime.now().isoformat()} | {summary}\n")

    # Show top new jobs
    for job in unique[:5]:
        title = job.get("title", "?")[:80]
        budget = "💰" if job.get("has_budget") else "  "
        print(f"  {budget} {title}")


if __name__ == "__main__":
    main()
