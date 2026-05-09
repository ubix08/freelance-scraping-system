# AI Freelance Scraping System

## Architecture
- **Layer 1 (script)** — `market_research.py`. Automated RSS collection, pre-filter, TTL dedup. Zero LLM cost.
- **3 commands, 3 agents:**

  | Command | Agent | Model | What it does |
  |---------|-------|-------|-------------|
  | `/scan` | `@analysis` | Haiku ($) | Examines collected jobs: requirements, complexity, deliverables, budget, confidence score |
  | `/propos` | `@proposal` | Sonnet ($$) | Writes winning Upwork proposals with sample-first + Loom strategy |
  | `/scrape` | `@scraper` | Sonnet ($$) | Recons target site, writes code, tests, delivers CSV |

## Workflow
1. `/collect` → collects jobs from Upwork
2. `/scan` → analyzes and validates the collected list
3. `/propos <job>` → writes the Upwork proposal
4. `/scrape <job>` → builds and delivers the scraper
5. `/log-job <outcome>` → tracks results

## Tool Selection
- Static HTML → `requests + BeautifulSoup`
- React/Vue/Angular → `Playwright + Chrome`
- Cloudflare → `curl_cffi`
- Heavy bot protection → DECLINE
