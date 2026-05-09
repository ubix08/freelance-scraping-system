# /full-pipeline — Run all agents on a single job

@.opencode/context/freelance/00-system-overview.md
@.opencode/context/freelance/agent-1-harvester.md
@.opencode/context/freelance/agent-2-intelligence.md
@.opencode/context/freelance/agent-3-synthesizer.md
@.opencode/context/freelance/agent-4-strategy.md
@.opencode/context/freelance/agent-5-proposals.md

Process this job through the complete pipeline:

1. **Agent 1 — Qualify**: ACCEPT/REJECT/HOLD with reason + complexity
2. **Agent 2 — Market**: Run 2 brave-search queries to validate demand and pricing
3. **Agent 3 — Offer**: Build 3-tier micro-offer with prices
4. **Agent 4 — Strategy**: If a target URL is given, run analyze_site.py on it. Otherwise determine likely strategy from job description.
5. **Agent 5 — Proposal**: Write complete copy-paste proposal (Template A — 0 reviews)

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
