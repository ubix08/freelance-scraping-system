# Master Project Specification — AI Freelance Scraping System

---

## 1. Project Overview

An AI-augmented freelance system that automatically **discovers**, **qualifies**, **analyzes**, and **bids on** web scraping/data extraction jobs. The system combines zero-cost Python automation scripts with OpenCode AI agents to create a pipeline that replaces a human freelancer's manual workflow.

**Goal**: $1,000/month from Upwork + Freelancer scraping gigs.

**Target VPS**: Contabo 4-core / 7GB RAM / Ubuntu 22.04.

---

## 2. System Architecture

### 2.1 Three-Layer Design

```
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 1 — Python Scripts (scripts/)                            │
│  $0 LLM cost. Runs on cron or command.                          │
│                                                                  │
│  discover_jobs.py  →  process_queue.py  →  analyze_site.py      │
│         │                  │                       │             │
│         ▼                  ▼                       ▼             │
│  raw_jobs.json    qualified_jobs.json    strategy report         │
├──────────────────────────────────────────────────────────────────┤
│  LAYER 2 — OpenCode Agents (.opencode/agents/)                  │
│  LLM-powered. Invoked via /command or @mention.                 │
│                                                                  │
│  @agent-0-discovery  (Haiku, low cost)   — job discovery        │
│  @agent-1-harvester  (Haiku, low cost)   — queue qualification  │
│  @agent-2-intelligence (Sonnet, moderate) — market intelligence │
│  @agent-3-synthesizer (Sonnet, moderate) — offer synthesis      │
│  @agent-4-strategy   (Sonnet, moderate)  — scraping strategy    │
│  @agent-5-proposals  (Sonnet, moderate)  — proposal writing     │
├──────────────────────────────────────────────────────────────────┤
│  LAYER 3 — Context Docs (.opencode/context/freelance/)          │
│  Reference knowledge base for agents.                           │
│                                                                  │
│  agent-0-discovery.md  →  discovery workflow reference          │
│  agent-1-harvester.md  →  job qualification rules               │
│  agent-2-intelligence.md  →  market research (Brave Search)     │
│  agent-3-synthesizer.md  →  offer/pricing logic                 │
│  agent-4-strategy.md  →  scraping strategy decision tree        │
│  agent-5-proposals.md  →  proposal templates and formulas       │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Inventory

| Component | File(s) | Language | Role |
|-----------|---------|----------|------|
| Job Discovery | `scripts/discover_jobs.py` | Python | RSS + API job collection |
| Queue Processor | `scripts/process_queue.py` | Python | Auto-qualification rules |
| Site Analyzer | `scripts/analyze_site.py` | Python | Recon, strategy, code prompts |
| Legacy Collector | `scripts/market_research.py` | Python | Original RSS collector |
| Master Orchestrator | `scripts/run_pipeline.py` | Python | Pipeline CLI controller |
| VPS Setup | `scripts/setup-vps.sh` | Bash | One-time infrastructure bootstrap |
| Cron Installer | `scripts/setup-cron.sh` | Bash | Schedule recurring discovery |
| OpenCode Config | `opencode.json` | JSON | MCP, instructions |
| Agent: Discovery | `.opencode/agents/agent-0-discovery.md` | Markdown | Job discovery agent |
| Agent: Harvester | `.opencode/agents/agent-1-harvester.md` | Markdown | Queue qualification agent |
| Agent: Intelligence | `.opencode/agents/agent-2-intelligence.md` | Markdown | Market intelligence agent |
| Agent: Synthesizer | `.opencode/agents/agent-3-synthesizer.md` | Markdown | Offer synthesis agent |
| Agent: Strategy | `.opencode/agents/agent-4-strategy.md` | Markdown | Scraping strategy agent |
| Agent: Proposals | `.opencode/agents/agent-5-proposals.md` | Markdown | Proposal writing agent |
| Commands (11) | `.opencode/commands/*.md` | Markdown | Slash commands for workflow |
| Context Docs (8) | `.opencode/context/freelance/*.md` | Markdown | Agent reference knowledge |

---

## 3. Core Data Flow

### 3.1 Full Pipeline

```
START
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  DISCOVER (Layer 1 — Script)                                 │
│                                                              │
│  discover_jobs.py:                                           │
│  ├── Upwork RSS (7 queries, $50+ min, fixed price)          │
│  ├── Freelancer API (4 queries, $20+ min, fixed price)      │
│  └── Deduplicates via seen_ids.json (MD5 of URL)            │
│                                                              │
│  Output: queue/raw_jobs.json                                 │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  QUALIFY (Layer 1 — Script)                                  │
│                                                              │
│  process_queue.py:                                           │
│  ├── REJECT  → no scraping keywords, low budget, CRM/Zapier │
│  ├── HOLD    → Cloudflare, captcha, login required           │
│  └── ACCEPT  → scraping match + budget ≥ $15 + no rejects   │
│      ├── Complexity: low/$75 / medium/$150 / high/$250       │
│      └── confidence scoring based on keyword signals         │
│                                                              │
│  Output: queue/qualified_jobs.json + queue/rejected_jobs.json│
└─────────────────────────────────────────────────────────────┘
  │
  ▼ (OpenCode agent reviews queue)
  │
┌─────────────────────────────────────────────────────────────┐
│  MARKET SCAN (Layer 2 — OpenCode Agent @analysis)            │
│                                                              │
│  Uses Brave Search MCP to:                                   │
│  ├── Validate niche demand                                   │
│  ├── Benchmark pricing (simple: $50-100, JS: $100-250, etc) │
│  ├── Identify winning differentiators                        │
│  └── Update job-tracker.md with findings                     │
│                                                              │
│  Tool: Brave Search API (requires free API key)              │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  SITE ANALYSIS (Layer 1 — Script)                            │
│                                                              │
│  analyze_site.py <TARGET_URL>:                               │
│  ├── Fetches page with realistic headers                     │
│  ├── Detects: JS frameworks (Next.js, Vue, React)            │
│  ├── Detects: anti-bot (Cloudflare, DataDome, Akamai, etc)  │
│  ├── Detects: pagination type (query/page/load_more/infinite)│
│  ├── Identifies: data selectors (product cards, prices)      │
│  ├── Recommends: tool (BS4 / Playwright / curl_cffi)         │
│  ├── Estimates: complexity + dev hours                       │
│  └── Generates: OpenCode starter prompt for scraper          │
│                                                              │
│  Output: strategy JSON + console report                      │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  OFFER SYNTHESIS (Layer 3 — Context-guided agent reasoning) │
│                                                              │
│  Agent synthesizes:                                          │
│  ├── 3-tier pricing (Core / Standard / Premium)              │
│  ├── base_price = max($50, hours × $35, rounded to $25)     │
│  ├── script_upsell = base + $35                              │
│  └── premium = base × 1.75                                   │
│                                                              │
│  Reference: agent-3-synthesizer.md                           │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  PROPOSAL (Layer 2 — OpenCode Agent @proposal)               │
│                                                              │
│  Writes Upwork proposal:                                     │
│  ├── Opening referencing exact problem                       │
│  ├── Sample-first strategy (10-20 row CSV sample)            │
│  ├── Technical approach (2 sentences)                        │
│  ├── Price + timeline                                        │
│  ├── Loom script (60-90 sec)                                 │
│  └── CTA question                                            │
│                                                              │
│  Output: jobs/{job_id}/proposal_{job_id}.md                  │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  BUILD SCRAPER (Layer 2 — OpenCode Agent @scraper)           │
│                                                              │
│  1. Recon target site (webfetch)                             │
│  2. Choose tool (BS4 / Playwright / curl_cffi)              │
│  3. Write scraper_{job_id}.py (rate-limited, error-handled) │
│  4. Test + debug                                             │
│  5. Deliver output_{job_id}.csv + README_{job_id}.md        │
│                                                              │
│  Output: jobs/{job_id}/scraper*.py, output*.csv, README*.md │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  LOG OUTCOME (Layer 2 — OpenCode Agent @proposal)            │
│                                                              │
│  /log-job won|active|delivered|lost {job_id} ${amount}       │
│  ├── Appends to queue/stats.json                             │
│  ├── Shows running totals (won, revenue, win rate)           │
│  └── Updates job-tracker.md dashboard                        │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
END (loop back to DISCOVER)
```

### 3.2 Two Parallel Workflows

The project has **two independent workflows** that share infrastructure:

#### Legacy Workflow (original)
- **Script**: `market_research.py` → **Queue**: `collected.json` → `validated.json`
- **Commands**: `/collect`, `/scan`, `/full-cycle`, `/propos`, `/scrape`
- **Agents**: `@analysis` handles scanning, `@proposal` handles proposals, `@scraper` handles building
- **Use case**: Single-agent job analysis + proposal + build

#### VPS Workflow (from zip)
- **Scripts**: `discover_jobs.py` → `process_queue.py` → **Queue**: `raw_jobs.json` → `qualified_jobs.json` / `rejected_jobs.json`
- **Commands**: `/discover`, `/qualify`, `/analyze-site`, `/market-scan`, `/full-pipeline`
- **Use case**: Batch automated discovery + qualification with human-in-the-loop review

---

## 4. Script Deep-Dive

### 4.1 `discover_jobs.py` — Agent 0: Job Hunter

**Purpose**: Collect raw job listings from public sources.

**Sources**:
| Source | Auth | Queries | Filter |
|--------|------|---------|--------|
| Upwork RSS | None (public feed) | 7 scraping terms | `budget=50-`, `job_type=fixed` |
| Freelancer API | None (public endpoint) | 4 scraping terms | `min_avg_price=20`, `project_types=fixed` |

**Deduplication**: MD5 hash of URL stored in `queue/seen_ids.json`. New jobs are merged into `queue/raw_jobs.json` as an append-only list.

**Rich console output**: Summary table showing Upwork vs Freelancer counts.

**Dependencies**: `feedparser`, `requests`, `rich`

### 4.2 `process_queue.py` — Agent 1: Opportunity Harvester

**Purpose**: Apply deterministic rules to accept, reject, or hold each job.

**Rule Engine**:
1. **REJECT if**: CRM keywords (salesforce/hubspot/n8n/zapier), ongoing/long-term contract language, budget < $15, no scraping keywords
2. **ACCEPT if**: At least one scraping keyword matched + no reject keywords + budget ≥ $15 or unspecified
3. **HOLD if**: Anti-bot signals (captcha, cloudflare, login, authenticated, bypass)

**Complexity Scoring**: Keyword-based signal detection
- **Low** ($75): simple, static, basic HTML, under 1000 rows
- **Medium** ($150): pagination, JS, login, large dataset
- **High** ($250+): captcha, Cloudflare, real-time, scheduled

**Budget Extraction**: Regex patterns for `$X-$Y`, `$X to $Y`, `budget: $X`.

**Output**: `qualified_jobs.json` (ACCEPT + HOLD), `rejected_jobs.json` (all rejects).

**Dependencies**: `rich`

### 4.3 `analyze_site.py` — Agent 4: Strategy Engine

**Purpose**: Given a target URL, determine exact scraping strategy.

**Detection Capabilities**:
| Detection | Method | Signals |
|-----------|--------|---------|
| JS Framework | Body text scan | `__NEXT_DATA__`, `__NUXT__`, `ng-app`, `react-root`, etc. |
| Anti-Bot | Headers + body | 6 tool fingerprints (Cloudflare, DataDome, Akamai, Imperva, Distil, PerimeterX) |
| Captcha | Body text | recaptcha, hcaptcha, challenge, etc. |
| Pagination | Body text + soup | 5 types: query_page, path_segment, load_more, infinite_scroll, numbered_links |
| Data Selectors | HTML parsing | Product cards, price fields, title tags (heuristic) |

**Strategy Selection Decision Tree**:
```
                     ┌─ Cloudflare/DataDome ──→ curl_cffi
                     │
is_dynamic? ─yes──┼─ No anti-bot ────────────→ Playwright
                     │
                     └─ Moderate anti-bot ────→ cloudscraper
                     
                     ┌─ No anti-bot ──────────→ BeautifulSoup
is_dynamic? ─no───┼─ Moderate anti-bot ────→ cloudscraper
                     │
                     └─ Heavy anti-bot ──────→ Playwright stealth
```

**Complexity Mapping**: `is_dynamic → medium`, `anti-bot moderate/heavy → high`, `Cloudflare/DataDome → very_high`

**Code Generation**: Produces a ready-to-paste OpenCode prompt with selectors, tool config, and requirements.

**Output**: JSON report saved to `/tmp/site_analysis_{domain}.json` + rich console output.

**Dependencies**: `requests`, `beautifulsoup4`, `lxml`, `rich`

### 4.4 `run_pipeline.py` — Master Orchestrator

**Purpose**: CLI frontend for running multiple scripts in sequence.

**Commands**:
| Command | Action |
|---------|--------|
| `discover` | Run `discover_jobs.py` |
| `qualify` | Run `process_queue.py` |
| `analyze` | Show top 3 accepted jobs with instructions to run site analysis |
| `show` | Display qualified jobs table with decision, complexity, price |
| `full` | Run discover + qualify + show sequentially |

**Dependencies**: `rich`

### 4.5 `market_research.py` — Legacy Collector

**Purpose**: Original lightweight RSS-only collector (predecessor to `discover_jobs.py`).

**Differences from `discover_jobs.py`**:
| Feature | `market_research.py` | `discover_jobs.py` |
|---------|---------------------|-------------------|
| Sources | Upwork RSS (4 queries) | Upwork RSS (7) + Freelancer API (4) |
| Min Budget | None explicit | Upwork: $50, Freelancer: $20 |
| Queue File | `collected.json` | `raw_jobs.json` |
| Dedup Method | URL-based + TTL (30 days) | MD5-based + persistent set |
| Output Format | Flat list with `has_budget` flag | Rich structure with source/id/query |

**Kept for backward compatibility** — the `/collect` and `/full-cycle` commands reference this script.

---

## 5. OpenCode Configuration (`opencode.json`)

### 5.1 Structure

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "brave-search": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
      "enabled": true,
      "environment": {
        "BRAVE_API_KEY": "YOUR_BRAVE_API_KEY_HERE"
      }
    }
  },
  "instructions": ["AGENTS.md"]
}
```

### 5.2 Components

1. **MCP — Brave Search**: Market intelligence searches. Requires free API key from https://api.search.brave.com/.
2. **Instructions**: `AGENTS.md` injected as system instructions into all agents — provides project rules, architecture overview, command reference, and tool selection guide.

Note: Commands are defined exclusively in `.opencode/commands/*.md` (11 files). Agent definitions are in `.opencode/agents/*.md` (3 files).

---

## 6. OpenCode Agents

### 6.1 `@agent-0-discovery` — Job Hunter (Haiku)

| Property | Value |
|----------|-------|
| Model | `claude-haiku-4-20250514` |
| Temp | 0.1 |
| Max Steps | 6 |
| Mode | Subagent |

**Permissions**:
| Resource | Access |
|----------|--------|
| Bash | `"*": deny` (except `python scripts/discover_jobs.py`, `python scripts/market_research.py`, `python scripts/run_pipeline.py discover`, `cat queue/raw_jobs.json`, `cat queue/collected.json`) |
| Read | Allow |
| Edit | Allow |
| Webfetch | Deny |
| Websearch | Deny |

**Role**: Run discovery scripts, read output, summarize new jobs found.

### 6.2 `@agent-1-harvester` — Opportunity Harvester (Haiku)

| Property | Value |
|----------|-------|
| Model | `claude-haiku-4-20250514` |
| Temp | 0.1 |
| Max Steps | 6 |
| Mode | Subagent |

**Permissions**:
| Resource | Access |
|----------|--------|
| Bash | `"*": deny` (except `python scripts/run_pipeline.py qualify`, `python scripts/run_pipeline.py show`, `cat queue/*.json`) |
| Read | Allow |
| Edit | Allow |
| Webfetch | Deny |
| Websearch | Deny |

**Role**: Process raw job queues — batch auto-qualify or manual qualification with accept/reject/hold decisions and complexity scoring.

### 6.3 `@agent-2-intelligence` — Market Intelligence (Sonnet)

| Property | Value |
|----------|-------|
| Model | `claude-sonnet-4-20250514` |
| Temp | 0.3 |
| Max Steps | 8 |
| Mode | Subagent |

**Permissions**:
| Resource | Access |
|----------|--------|
| Bash | `"*": deny` |
| Read | Allow |
| Edit | Allow |
| Websearch | Allow |

**Role**: Use Brave Search MCP to validate demand, benchmark pricing, identify differentiators. Update job-tracker.md.

### 6.4 `@agent-3-synthesizer` — Offer Synthesizer (Sonnet)

| Property | Value |
|----------|-------|
| Model | `claude-sonnet-4-20250514` |
| Temp | 0.3 |
| Max Steps | 6 |
| Mode | Subagent |

**Permissions**:
| Resource | Access |
|----------|--------|
| Bash | `"*": deny` |
| Read | Allow |
| Edit | Allow |
| Webfetch | Deny |
| Websearch | Deny |

**Role**: Convert qualified job + strategy analysis into 3-tier micro-offer with formula-based pricing.

### 6.5 `@agent-4-strategy` — Strategy Analyzer (Sonnet)

| Property | Value |
|----------|-------|
| Model | `claude-sonnet-4-20250514` |
| Temp | 0.2 |
| Max Steps | 15 |
| Mode | Subagent |

**Permissions**:
| Resource | Access |
|----------|--------|
| Bash | `"*": ask` (except `python scripts/analyze_site.py *` allow, `pip install *` allow, `mkdir *` allow) |
| Read | Allow |
| Edit | Allow |
| Webfetch | Allow |
| Glob | Allow |
| Grep | Allow |

**Role**: Site recon → tool selection → scraper code generation → test → deliver CSV + README.

### 6.6 `@agent-5-proposals` — Proposal Writer (Sonnet)

| Property | Value |
|----------|-------|
| Model | `claude-sonnet-4-20250514` |
| Temp | 0.4 |
| Max Steps | 10 |
| Mode | Subagent |

**Permissions**:
| Resource | Access |
|----------|--------|
| Bash | `"*": deny` (except `cat queue/validated.json`, `cat queue/qualified_jobs.json`, `mkdir *`) |
| Read | Allow |
| Edit | Allow |

**Role**: Write Upwork proposals with sample-first strategy, Loom scripts, outcome-based pricing. Handle job logging.

---

## 7. Commands Reference

### 7.1 All 11 Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/collect` | `agent-0-discovery` | Run `market_research.py`, report new jobs |
| `/scan` | `agent-1-harvester` | Read `collected.json`, assign confidence scores, save to `validated.json` |
| `/full-cycle` | `agent-0-discovery` | Collect + scan in one step |
| `/propos` | `agent-5-proposals` | Write Upwork proposal for a job |
| `/log-job` | `agent-5-proposals` | Track job outcome (won/lost/delivered) |
| `/scrape` | `agent-4-strategy` | Build + test a scraper |
| `/discover` | `agent-0-discovery` | Run `discover_jobs.py` (Upwork + Freelancer) |
| `/qualify` | `agent-1-harvester` | Run `process_queue.py` to auto-qualify raw queue |
| `/analyze-site` | `agent-4-strategy` | Run `analyze_site.py` on a target URL |
| `/market-scan` | `agent-2-intelligence` | Weekly market intelligence via Brave Search |
| `/full-pipeline` | `agent-4-strategy` | End-to-end: qualify → market → offer → strategy → proposal |

### 7.2 Command File Format

Each command file in `.opencode/commands/` uses YAML frontmatter:
```yaml
---
description: Human-readable description
agent: agent-0-discovery|agent-1-harvester|agent-2-intelligence|agent-3-synthesizer|agent-4-strategy|agent-5-proposals
subtask: true
---
Template body... ($ARGUMENTS for user input)
```

---

## 8. Context Documentation System

The `.opencode/context/freelance/` directory contains 8 reference files that agents can use as knowledge sources. These are NOT OpenCode agent definitions — they are documentation files loaded by agents during task execution.

### 8.1 File Index

| File | Content |
|------|---------|
| `00-system-overview.md` | Full system architecture diagram, VPS resource budget, tool hierarchy, income goal tracker |
| `agent-0-discovery.md` | Discovery script usage, scheduling, expansion guide |
| `agent-1-harvester.md` | Qualification rules (ACCEPT/REJECT/HOLD checklists), complexity scoring, output format |
| `agent-2-intelligence.md` | Brave Search query sequences, pricing benchmarks, output JSON schema |
| `agent-3-synthesizer.md` | 3-tier pricing formula, standard offer library (4 types), offer output schema |
| `agent-4-strategy.md` | Site analysis interpretation decision tree, execution plan template, code templates for BS4/Playwright/curl_cffi |
| `agent-5-proposals.md` | Proposal formulas (3 templates for 0 reviews / with reviews / competitive), delivery note template |
| `job-tracker.md` | Dashboard with earned/active/proposals/win rate, active jobs table, weekly market intelligence section |

---

## 9. Data Model

### 9.1 Queue Files

| File | Format | Schema |
|------|--------|--------|
| `queue/collected.json` | Array | `[{title, url, description, source, posted, has_budget, discovered_at}]` |
| `queue/validated.json` | Array | Same as collected with added `{analysis: {confidence, complexity, requirements, budget_sanity, deliverables}}` |
| `queue/raw_jobs.json` | Array | `[{source, id, title, description, url, published, query_used, fetched_at}]` |
| `queue/qualified_jobs.json` | Array | Same as raw with added `{qualification: {decision, complexity, matched_keywords, estimated_hours, suggested_price}}` |
| `queue/rejected_jobs.json` | Array | Same as raw with added `{qualification: {decision: "REJECT", reason}}` |
| `queue/seen_ids.json` | Array | `[{url, timestamp}]` (legacy) or `[md5_hash_strings]` (new) |
| `queue/stats.json` | Array | `[{job_id, title, budget, connects_spent, status, notes}]` |

### 9.2 Legacy vs. New Queue File Mapping

| Legacy (market_research.py) | New (discover_jobs.py pipeline) |
|-----------------------------|----------------------------------|
| `collected.json` | `raw_jobs.json` |
| `validated.json` | `qualified_jobs.json` |
| — | `rejected_jobs.json` |
| `seen_ids.json` (URL + TTL) | `seen_ids.json` (MD5, persistent) |

### 9.3 Job Output Files

```
jobs/{job_id}/
├── proposl_{job_id}.md     (from @proposal)
├── scraper_{job_id}.py     (from @scraper)
├── output_{job_id}.csv     (from @scraper)
└── README_{job_id}.md      (from @scraper)
```

---

## 10. Pricing Model

### 10.1 Complexity-Based Pricing (process_queue.py)

| Complexity | Price | Signals |
|------------|-------|---------|
| Low | $75 | Static HTML, simple CSV, under 1000 rows, one-time |
| Medium | $150 | Pagination, JS rendering, login, 10k+ rows |
| High | $250+ | Cloudflare, captcha, real-time, scheduled |
| Very High | $300+ | Heavy anti-bot, multi-source, complex scheduling |

### 10.2 Formula-Based Pricing (agent-3-synthesizer.md)

```
base_price = max($50, estimated_hours × $35/hr)
round base_price to nearest $25
script_upsell = base_price + $35
premium_tier  = base_price × 1.75
```

### 10.3 Standard Offer Library

| Offer | Data Type | Price | Hours | Tool |
|-------|-----------|-------|-------|------|
| A — Static Product Scraping | Product names, prices, SKUs, images | $75–$125 | 2–4 | BeautifulSoup |
| B — Directory/Lead List | Name, email, phone, address, URL | $100–$175 | 3–6 | BS4 or Playwright |
| C — JS-Rendered Site | JS-heavy data (React, Vue, Angular) | $150–$275 | 5–10 | Playwright |
| D — Data Cleaning | Messy spreadsheet → clean CSV | $50–$100 | 2–4 | Pandas |

---

## 11. VPS Deployment

### 11.1 Setup Script (`scripts/setup-vps.sh`)

Installs:
- **System pkgs**: Python3, Node.js, Chrome dependencies, xvfb
- **Python env**: `~freelance-env` venv with 14 packages (requests, beautifulsoup4, playwright, scrapy, selenium, pandas, cloudscraper, curl-cffi, etc.)
- **Playwright**: Chromium browser for Playwright automation
- **Node.js**: Brave Search MCP server, Playwright
- **Project dirs**: `jobs/`, `queue/`, `scripts/`, `logs/`, `.opencode/context/freelance/`, `.opencode/commands/`

### 11.2 Resource Budget

| Process | CPU | RAM | Max Concurrent |
|---------|-----|-----|----------------|
| OpenCode runtime | 1 core | ~500MB | 1 |
| Playwright/Chrome | 1 core | ~400MB | 3 |
| BeautifulSoup | 0.5 core | ~100MB | 8+ |
| Scrapy | 1 core | ~200MB | 4 |
| **Total safe** | 3.5 cores | ~5.5GB | — |

### 11.3 Cron Schedule

```bash
# setup-cron.sh installs:
0 8,14 * * 1-5  cd ~/freelance-system && .../python scripts/market_research.py >> logs/market_research.log
```

---

## 12. Tool Selection Decision Tree

```
Static HTML → requests + BeautifulSoup
    ↓ Fastest, most stable, lowest resource usage

JS-rendered (React, Vue, Angular) → Playwright + Chrome (VPS)
    ↓ Executes JS, uses local Chrome binary

Cloudflare / TLS-fingerprint → curl_cffi (impersonate chrome120)
    ↓ Mimics Chrome TLS fingerprint, bypasses basic CF

Basic JS challenge → cloudscraper
    ↓ Lightweight Cloudflare bypass, no browser needed

Login-required → Playwright with session cookies
    ↓ Session persistence for authenticated pages

Heavy protection (Akamai, DataDome, PerimeterX) → DECLINE
    ↑ Too risky for $100-300 freelance gigs
```

---

## 13. Edge Cases, Risks, and Observations

### 13.1 Identified During Review

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Duplicate queue files** — Two parallel queue sets (`collected`/`validated` vs `raw`/`qualified`) | Low | Documented in AGENTS.md; commands correctly reference their respective files |
| **Rich dependency** — New scripts (`discover_jobs.py`, `process_queue.py`, `analyze_site.py`, `run_pipeline.py`) require `rich` | Low | Included in `setup-vps.sh` pip install list |
| **Legacy script still active** — `market_research.py` vs new `discover_jobs.py` do similar things to different queue files | Low | Both are functional; user can choose workflow |
| **Market_research.py misspelling** — Script named `market_research.py` (missing 'a') | Cosmetic | All references use correct filename; changing would break references |
| **No data validation** — Scripts assume well-formed JSON in queue files | Medium | All scripts handle missing files gracefully; JSON parse errors caught |
| **PAT in git remote URL** — Token hardcoded in `.git/config` | **High** | Already flagged; user should revoke and migrate to `gh auth` |
| **Empty `.opencode/context/` is not an OpenCode standard directory** | Low | It's a custom project convention for reference docs; agents use them via command templates |
| **Queue files initialized as `[]`** — Manual creation needed for non-legacy files (`raw_jobs.json`, `qualified_jobs.json`, `rejected_jobs.json`) | Low | VPS setup script creates directories; files created on first script run |
| **analyze_site.py uses `/tmp/`** — Report saved to `/tmp/site_analysis_*.json` which is volatile | Low | Temp file may be lost on reboot; console output is primary |

### 13.2 Missing / Recommended Additions

1. **.env file** — API keys (Brave Search) should be in `.env`, not `opencode.json`
2. **GitHub Actions CI** — Lint Python scripts on push
3. **Unit tests** — No tests exist for any script; `process_queue.py` rule engine is a prime candidate
4. **Logging** — Scripts use `print`/`rich` instead of Python logging module
5. **Rate limiting** — No global rate limiter across parallel scrapers
6. **Error alerting** — No mechanism to alert user if pipeline fails (e.g., Upwork RSS changes format)

---

## 14. Configuration Quick Reference

### 14.1 Files That Control Behavior

| File | What It Controls |
|------|-----------------|
| `opencode.json` | MCP servers, instruction files |
| `.opencode/agents/*.md` | Agent model, permissions, system prompt |
| `.opencode/commands/*.md` | Available slash commands and their templates |
| `.opencode/context/freelance/*.md` | Agent reference knowledge |
| `AGENTS.md` | Project-level instructions (loaded via `instructions`) |
| `scripts/process_queue.py` | Auto-qualification rules (ACCEPT/REJECT keywords, pricing) |
| `scripts/discover_jobs.py` | Discovery sources (Upwork queries, Freelancer queries) |
| `scripts/analyze_site.py` | Detection patterns, tool recommendations, code generation |
| `scripts/setup-vps.sh` | VPS dependencies, Python packages, Chrome |

---

*End of Master Specification. 36 files reviewed across 3 layers: 7 scripts, 6 agents, 11 commands, 8 context docs, 2 config files, 2 shell scripts, 2 deployment/meta docs.*
