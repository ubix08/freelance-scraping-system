---
description: Analyze a target URL to determine scraping strategy and tool selection
agent: scraper
subtask: true
---

Analyze the target site and determine scraping strategy.

Run:
```bash
source ~/freelance-env/bin/activate && python scripts/analyze_site.py $ARGUMENTS
```

After the script runs, read the JSON output and produce:
1. Tool recommendation with reason
2. Complexity and feasibility verdict
3. The complete execution plan (phases 1-6)
4. The exact OpenCode prompt to generate the scraper
5. Price floor based on complexity

URL to analyze:
$ARGUMENTS
