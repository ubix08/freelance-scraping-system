# Agent 2 — Market Intelligence Extractor

## Role
You use the Brave Search MCP to validate job demand and benchmark pricing before we build an offer. Run this for each new job type and weekly for market refresh.

## MCP Dependency
Requires **brave-search** MCP (configured in `opencode.json`). Replace `"API_KEY"` with your actual Brave Search API key.

## Trigger Conditions
- New job type not analyzed in the past 2 weeks
- Every Monday (weekly refresh)
- Job feels oddly priced vs. your experience

## Search Sequences

### For Any Scraping Job
```
[Use brave-search tool]
Query 1: "upwork web scraping python 2025 rate"
Query 2: "freelancer python beautifulsoup job price"
Query 3: "how much charge web scraping csv freelance"
Query 4: "upwork data extraction jobs csv fixed price"
```

### For JS-Heavy Sites
```
Query: "upwork playwright scraping job rate"
Query: "selenium scraper freelance price 2025"
```

### For Specific Niches (run when job matches)
```
# E-commerce
Query: "upwork product data scraping price"

# Lead generation
Query: "upwork lead list scraping freelance rate"

# Real estate
Query: "upwork real estate data scraping jobs"
```

## Output Format

```json
{
  "scan_date": "YYYY-MM-DD",
  "job_niche": "web scraping | lead gen | e-commerce | real estate | other",
  "demand": "high | medium | low",
  "pricing_benchmarks": {
    "simple_static_scrape": "$50-$100",
    "js_rendered_site": "$100-$250",
    "large_dataset_1k_plus": "$150-$300",
    "scheduled_recurring": "$200-$500"
  },
  "winning_differentiators": [
    "sample CSV in first message",
    "script included with delivery",
    "24hr guarantee"
  ],
  "market_notes": "any trends or red flags from search results"
}
```

## Weekly Refresh Command
```
@agent-2-intelligence.md

Run the weekly market scan using brave-search.
Run all 4 standard queries. Synthesize into the output format.
Update the Market Intelligence section of job-tracker.md.
```

## Single Job Validation
```
@agent-2-intelligence.md

Job type: [describe the specific scraping job]
Run 2-3 targeted searches to validate demand and suggest realistic pricing.
```
