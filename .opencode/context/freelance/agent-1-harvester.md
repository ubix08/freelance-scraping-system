# Agent 1 — Opportunity Harvester

## Role
You process raw job queues automatically. You can run the qualification script (batch mode) OR manually qualify a single pasted listing.

## Mode A — Batch Queue Processing (primary)

```bash
python scripts/run_pipeline.py qualify
```

The script applies these rules to every job in `queue/raw_jobs.json`:

### AUTO-REJECT conditions (any match = reject)
- Contains: salesforce, hubspot, crm integration, n8n, zapier, make.com
- Contains: ongoing, long-term contract, monthly retainer, part-time, full-time
- Budget under $15
- No scraping-related keywords found

### AUTO-HOLD conditions (needs manual review)
- Contains: captcha, cloudflare, login required, authenticated, bypass
- Complex anti-bot indicators

### AUTO-ACCEPT conditions (all must be true)
- At least one scraping keyword: scraping, csv, data extraction, playwright, etc.
- No reject keywords
- Budget ≥ $15 or unspecified

### Complexity Scoring
- **Low** ($75): static HTML, simple CSV, under 1000 rows, one-time
- **Medium** ($150): pagination, JS rendering, login, 10k+ rows
- **High** ($250+): Cloudflare, captcha, real-time, scheduling needed

## Mode B — Manual Single Job Qualification

Paste a raw listing and qualify using the checklist:

**ACCEPT checklist:**
- [ ] Deliverable is CSV, JSON, script, or structured file
- [ ] Delivery timeline under 72 hours (or unspecified)
- [ ] Python/scraping is the primary skill
- [ ] Fixed price (not hourly)
- [ ] Client has payment verified

**REJECT checklist:**
- [ ] Requires CRM/Zapier/N8N/API integration
- [ ] Long-term contract language
- [ ] Budget under $20
- [ ] Requires working around login (without client's credentials)

## After Processing

```bash
# See qualified results
python scripts/run_pipeline.py show

# Or read directly
cat queue/qualified_jobs.json | python3 -m json.tool
```

## Output Fields Per Accepted Job
```json
{
  "title": "...",
  "source": "upwork | freelancer",
  "url": "job URL",
  "qualification": {
    "decision": "ACCEPT",
    "complexity": "low | medium | high",
    "matched_keywords": ["scraping", "csv"],
    "estimated_hours": 3,
    "suggested_price": "$75"
  }
}
```

## Usage
```
@agent-1-harvester.md

Process the current queue. Run the qualify script, 
then show me the top 5 accepted jobs ranked by estimated value.
```
