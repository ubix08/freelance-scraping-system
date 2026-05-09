# /qualify — Agent 1: Filter the queue

@.opencode/context/freelance/agent-1-harvester.md
@.opencode/context/freelance/job-tracker.md

Run queue qualification. Execute:
```bash
source ~/freelance-env/bin/activate && python scripts/run_pipeline.py qualify
```
Then show the top 10 accepted jobs with title, complexity, and suggested price.
Rank by estimated value (suggested_price × feasibility).
