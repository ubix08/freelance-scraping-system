# Agent 0 — Job Discovery

## Role
You are the job hunter. You run the Python discovery script on the VPS to collect raw job listings from Upwork and Freelancer, then report what was found.

## Execution

```bash
# Run from the project root on VPS
source ~/freelance-env/bin/activate
python scripts/discover_jobs.py
```

Or via the master runner:
```bash
python scripts/run_pipeline.py discover
```

## What the Script Does
1. Queries Upwork RSS feeds with 7 scraping-related search terms (no auth required)
2. Queries Freelancer's public API with 4 search terms
3. Deduplicates against `queue/seen_ids.json` (never shows same job twice)
4. Saves raw listings to `queue/raw_jobs.json`

## Output Review

After running, read the queue:
```bash
cat queue/raw_jobs.json | python3 -m json.tool | head -100
```

Or ask OpenCode:
```
Run Agent 0 discovery. Then read queue/raw_jobs.json and tell me:
- How many new jobs found
- Top 5 most promising by title
- Any unusual job types worth noting
```

## Scheduling on VPS (Optional)

Set up a cron to run twice daily:
```bash
crontab -e

# Add:
0 8,18 * * * cd ~/freelance-system && source ~/freelance-env/bin/activate && python scripts/discover_jobs.py >> logs/discovery.log 2>&1
```

## Expanding Discovery Sources

To add more sources, edit `scripts/discover_jobs.py`:
- Add `UPWORK_QUERIES` entries for new job types
- Add `FREELANCER_QUERIES` entries
- Add new functions for PeoplePerHour, Guru, Toptal if needed

## Usage in OpenCode
```
@agent-0-discovery.md

Run job discovery now. Execute the script, read the output, 
and summarize the top 10 new jobs found.
```
