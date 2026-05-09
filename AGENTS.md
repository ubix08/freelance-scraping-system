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
| `@analysis` | Haiku ($) | Job qualification, market scanning, analysis |
| `@proposal` | Sonnet ($$) | Proposal writing, job logging |
| `@scraper` | Sonnet ($$) | Site recon, scraper building, testing |

### Layer 3 — Context Docs (`.opencode/context/freelance/`)
Reference docs for pipeline agents 0–5 (discovery, harvester, intelligence, synthesizer, strategy, proposals) plus system overview and job tracker.

## Commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/collect` | analysis | Run market_research.py, report new jobs |
| `/scan` | analysis | Examine collected.json, assign confidence scores |
| `/propos` | proposal | Write Upwork proposal for a job |
| `/scrape` | scraper | Build + test a scraper |
| `/full-cycle` | analysis | Collect + scan in one command |
| `/log-job` | proposal | Track job outcome (won/lost/delivered) |
| `/discover` | analysis | Run discover_jobs.py (Upwork + Freelancer) |
| `/qualify` | analysis | Auto-qualify raw queue |
| `/analyze-site` | scraper | Analyze a target URL for scraping strategy |
| `/market-scan` | analysis | Weekly market intelligence via Brave Search |
| `/full-pipeline` | scraper | End-to-end pipeline: qualify → market → offer → strategy → proposal |

## Tool Selection
- Static HTML → `requests + BeautifulSoup`
- React/Vue/Angular → `Playwright + Chrome`
- Cloudflare → `curl_cffi`
- Heavy bot protection → DECLINE
