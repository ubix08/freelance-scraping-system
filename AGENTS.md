# AI Freelance Scraping System

## Architecture

### Layer 1 — Scripts (`scripts/`)
Automated Python scripts that run locally or on a VPS. Zero LLM cost.

| Script | Purpose |
|--------|---------|
| `discover_jobs.py` | Upwork RSS (7 queries) + Freelancer API (4 queries) → `queue/raw_jobs.json` |
| `process_queue.py` | Auto-qualify: keyword match, complexity score, budget filter → `queue/qualified_jobs.json` |
| `analyze_site.py` | Site recon: tech stack, anti-bot, pagination → tool recommendation |
| `run_pipeline.py` | Master orchestrator for discover/qualify/full pipeline |
| `market_research.py` | Original lightweight RSS collector → `queue/collected.json` |

### Layer 2 — OpenCode Agents (`.opencode/agents/`)

| Agent | Model | Role |
|-------|-------|------|
| `@agent-0-discovery` | Haiku ($) | Job discovery — runs RSS + API collection scripts |
| `@agent-1-harvester` | Haiku ($) | Queue qualification — accept/reject/hold + complexity scoring |
| `@agent-2-intelligence` | Sonnet ($$) | Market intelligence — Brave Search pricing validation |
| `@agent-3-synthesizer` | Sonnet ($$) | Offer synthesis — 3-tier micro-offer with pricing |
| `@agent-4-strategy` | Sonnet ($$) | Scraping strategy — site recon, tool selection, code generation |
| `@agent-5-proposals` | Sonnet ($$) | Proposal writing — sample-first, Loom scripts, outcome pricing |

### Layer 3 — Context Docs (`.opencode/context/freelance/`)
Reference docs for pipeline agents 0–5 (discovery, harvester, intelligence, synthesizer, strategy, proposals) plus system overview and job tracker.

## Commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/collect` | agent-0-discovery | Run market_research.py, report new jobs |
| `/scan` | agent-1-harvester | Examine collected.json, assign confidence scores |
| `/propos` | agent-5-proposals | Write Upwork proposal for a job |
| `/scrape` | agent-4-strategy | Build + test a scraper |
| `/full-cycle` | agent-0-discovery | Collect + scan in one command |
| `/log-job` | agent-5-proposals | Track job outcome (won/lost/delivered) |
| `/discover` | agent-0-discovery | Run discover_jobs.py (Upwork + Freelancer) |
| `/qualify` | agent-1-harvester | Auto-qualify raw queue |
| `/analyze-site` | agent-4-strategy | Analyze a target URL for scraping strategy |
| `/market-scan` | agent-2-intelligence | Weekly market intelligence via Brave Search |
| `/full-pipeline` | agent-4-strategy | End-to-end pipeline: qualify → market → offer → strategy → proposal |

## Tool Selection
- Static HTML → `requests + BeautifulSoup`
- React/Vue/Angular → `Playwright + Chrome`
- Cloudflare → `curl_cffi`
- Heavy bot protection → DECLINE
