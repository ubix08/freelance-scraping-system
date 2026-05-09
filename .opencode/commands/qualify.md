---
description: Auto-qualify raw job queue — accept, reject, or hold
agent: agent-1-harvester
subtask: true
---

Run queue qualification:
```bash
source ~/freelance-env/bin/activate && python scripts/run_pipeline.py qualify
```
Then show the top 10 accepted jobs with title, complexity, and suggested price. Rank by estimated value (suggested_price × feasibility).
