---
description: Run the complete pipeline — qualify, market check, offer, strategy, proposal
agent: scraper
subtask: true
---

Process this job through the complete pipeline:

1. **Qualify**: ACCEPT/REJECT/HOLD with reason + complexity
2. **Market**: Run 2 brave-search queries to validate demand and pricing
3. **Offer**: Build 3-tier micro-offer with prices
4. **Strategy**: If a target URL is given, run analyze_site.py on it. Otherwise determine likely strategy from job description.
5. **Proposal**: Write complete copy-paste proposal

End with a PIPELINE SUMMARY block:
```
━━━ PIPELINE SUMMARY ━━━
Decision:    ACCEPT / REJECT / HOLD
Tool:        beautifulsoup / playwright / curl_cffi
Complexity:  low / medium / high
My Price:    $X
Deliver in:  N hours
Proposal:    ready to paste
Next action: [submit / build sample first / skip]
```

Job listing:
$ARGUMENTS
