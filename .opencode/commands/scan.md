---
description: Analyze collected jobs: requirements, complexity, deliverables, budget
agent: analysis
subtask: true
---

Read `queue/collected.json`. Examine every un-analyzed job:

1. What exactly needs scraping — specific pages, data fields, volume
2. Complexity — low (static HTML), medium (JS/pagination), high (anti-bot/login), unknown
3. Deliverables — what a winning bid must produce
4. Budget sanity — is the implied budget realistic?

Assign a confidence score (1-5) to each. Save results to `queue/validated.json` with your reasoning. Show a ranked summary table.
