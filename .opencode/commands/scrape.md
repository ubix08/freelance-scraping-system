---
description: Build and test a scraper for a validated job
agent: agent-4-strategy
subtask: true
---

Build a scraper for: $ARGUMENTS. Check `queue/validated.json` for prior analysis if available.

Process:
1. **Recon** — webfetch the target site. Determine tech stack, anti-bot, pagination
2. **Plan** — choose BS4 / Playwright / curl_cffi with justification
3. **Build** — write `jobs/{job_id}/scraper_{job_id}.py` with rate limiting, error handling, CSV export
4. **Test** — run it, debug any errors
5. **Deliver** — save `output_{job_id}.csv` + `README_{job_id}.md`
