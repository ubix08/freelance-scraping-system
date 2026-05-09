# AI Freelance Scraping System — 2-Layer Architecture

## Overview

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1 — Market Research (automated Python script)    │
│  python scripts/market_research.py                      │
│  Collects scraping jobs from Upwork RSS, pre-filters,   │
│  deduplicates with 30-day TTL. Zero LLM cost.           │
│  Runs on cron or via /collect.                          │
│  Output: queue/collected.json                           │
├─────────────────────────────────────────────────────────┤
│  Merged Layer 2+3 — Web Scraping Specialist (agent)      │
│  @scraper agent (Sonnet)                                │
│  Invoked via /scan.                                      │
│  Single agent handling the full flow:                    │
│  • Examines collected job list (requirements,            │
│    complexity, deliverables, budget)                     │
│  • Assigns confidence scores 1-5                         │
│  • Recons target site (webfetch)                        │
│  • Plans scraping approach                              │
│  • Writes, tests, and delivers the scraper              │
│  Output: queue/validated.json + jobs/{job_id}/           │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
~/freelance-system/
├── opencode.json                    # Single agent + 4 commands
├── AGENTS.md                        # Project rules
├── DEPLOYMENT-GUIDE.md
│
├── scripts/
│   ├── market_research.py           # Layer 1: only Python script
│   ├── setup-vps.sh                 # One-time VPS bootstrap
│   └── setup-cron.sh                # Daily cron (8AM + 2PM)
│
├── .opencode/
│   └── commands/
│       ├── collect.md               # Layer 1
│       ├── scan.md                  # Merged Layer 2+3
│       ├── full-cycle.md            # Both layers
│       └── log-job.md               # Track outcomes
│
├── queue/
│   ├── collected.json               # Raw collected jobs
│   ├── validated.json               # LLM-analyzed jobs
│   ├── stats.json                   # Win/loss tracking
│   └── seen_ids.json                # Dedup with 30-day TTL
│
├── jobs/
│   └── {job_id}/
│       ├── scraper_{job_id}.py
│       ├── output_{job_id}.csv
│       └── README_{job_id}.md
│
└── logs/
    └── market_research.log
```

## Quick Start

```bash
# VPS setup
ssh user@contabo-vps
git clone <repo> ~/freelance-system && cd ~/freelance-system
bash scripts/setup-vps.sh
bash scripts/setup-cron.sh
source ~/freelance-env/bin/activate
python scripts/market_research.py

# Local OpenCode
curl -fsSL https://opencode.ai/install | bash
cd ~/freelance-system && opencode
```

## Daily Workflow

| Step | Command | What Happens | Cost |
|------|---------|-------------|------|
| 1 | `/collect` | Scans Upwork, pre-filters, dedup | $0 |
| 2 | `/scan` | Agent examines + analyzes + builds | ~$0.50-2 (Sonnet) |
| 3 | `/log-job won "JobX $150 20c"` | Track outcome | ~$0.01 |

## Design Rationale

**Why merge Layer 2 and 3?** The analysis phase (what's needed, complexity, budget) and the build phase (writing the scraper) are tightly coupled. A single agent with the full context — job requirements + site analysis + code — makes better decisions than splitting them. One `/scan` command, one agent, end to end.

**Why only one Python script?** Everything the agent needs that doesn't require reasoning (RSS polling, dedup, TTL management) lives in `market_research.py`. Everything that needs judgment (is this doable? what approach? is the budget fair?) lives in the LLM agent.

**Single agent, single source of truth.** No dual definitions. `opencode.json` is the only place agents are defined. `.opencode/agents/` is intentionally empty.
