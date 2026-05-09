# AI Freelance Scraping System — VPS Edition
## Contabo VPS: 4 Core / 7GB RAM | OpenCode + Local Chrome

## System Architecture

```
VPS (Contabo)
│
├── OpenCode Agent Runtime
│   ├── Brave Search MCP          ← market intelligence
│   ├── Bash Tool                 ← execute Python scripts
│   └── File R/W                  ← queue, job tracker
│
├── Python Scripts (scripts/)
│   ├── discover_jobs.py          ← Agent 0: Upwork RSS + Freelancer API
│   ├── process_queue.py          ← Agent 1: auto-qualify 200+ jobs/run
│   ├── analyze_site.py           ← Agent 4: site analysis + strategy engine
│   └── run_pipeline.py           ← master orchestrator
│
├── Chrome (headless)             ← Playwright scraping on VPS
│   └── /usr/bin/google-chrome
│
└── queue/
    ├── raw_jobs.json             ← unfiltered discovered jobs
    ├── qualified_jobs.json       ← ACCEPT + HOLD after Agent 1
    └── rejected_jobs.json        ← filtered out
```

## Full Pipeline Flow

```
[CRON / MANUAL TRIGGER]
        ↓
Agent 0 — discover_jobs.py
  Upwork RSS (7 queries) + Freelancer API (4 queries)
  → raw_jobs.json
        ↓
Agent 1 — process_queue.py
  Keyword matching + complexity scoring + budget filter
  → qualified_jobs.json
        ↓
[OpenCode reviews qualified_jobs.json]
        ↓
Agent 2 — Market Intelligence (Brave Search MCP)
  Validates demand and pricing per job type
        ↓
Agent 3 — Offer Synthesizer
  Builds micro-offer with tiered pricing
        ↓
Agent 4 — analyze_site.py [target URL]
  Detects: static/JS/anti-bot/pagination
  Selects: BS4 / Playwright / curl_cffi / cloudscraper
  Outputs: starter code prompt
        ↓
Agent 5 — Proposal Generator
  Writes copy-paste Upwork proposal
        ↓
[DELIVER → REVIEW → LOG → REPEAT]
```

## VPS Resource Budget (4 core / 7GB)

| Process | CPU | RAM | Concurrent |
|---------|-----|-----|------------|
| OpenCode | 1 core | ~500MB | 1 |
| Chrome (Playwright) | 1 core | ~400MB/instance | max 3 |
| Python BS4 scraper | 0.5 core | ~100MB | 4+ |
| Scrapy spider | 1 core | ~200MB | 2 |
| **Total safe budget** | 3.5 core | ~5.5GB | — |

## Scraping Tool Hierarchy (by target site type)

```
Site type                    → Best tool
─────────────────────────────────────────────
Static HTML                  → requests + BeautifulSoup
JS-rendered (React/Vue)      → Playwright + Chromium (local Chrome)
Cloudflare / TLS-fingerprint → curl_cffi (impersonate Chrome)
Basic JS challenge           → cloudscraper
Login-required               → Playwright with session cookies
Heavily protected (Akamai)   → HOLD for manual review
```

## Income Goal Tracker
**Current: $0 / $1,000**
