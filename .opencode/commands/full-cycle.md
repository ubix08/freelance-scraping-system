---
description: Collect + scan in one command
agent: agent-0-discovery
subtask: true
---

Run `python scripts/market_research.py`. Then read `queue/collected.json` and scan every job: requirements, complexity, deliverables, budget, confidence scores. Save to `queue/validated.json`. Show ranked summary.
