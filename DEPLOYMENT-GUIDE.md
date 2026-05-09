# AI Freelance Scraping System — VPS Deployment Guide
## Contabo VPS: 4 Core / 7GB RAM | OpenCode + Local Chrome

---

## 📁 Full Project Structure

```
~/freelance-system/
├── opencode.json                            # OpenCode config
├── DEPLOYMENT-GUIDE.md                      # This file
│
├── scripts/
│   ├── setup-vps.sh                         # One-time VPS setup
│   ├── discover_jobs.py                     # Agent 0: job hunter
│   ├── process_queue.py                     # Agent 1: qualifier
│   ├── analyze_site.py                      # Agent 4: strategy engine
│   └── run_pipeline.py                      # Master orchestrator
│
├── .opencode/
│   ├── context/freelance/
│   │   ├── 00-system-overview.md
│   │   ├── agent-0-discovery.md
│   │   ├── agent-1-harvester.md
│   │   ├── agent-2-intelligence.md
│   │   ├── agent-3-synthesizer.md
│   │   ├── agent-4-strategy.md
│   │   ├── agent-5-proposals.md
│   │   └── job-tracker.md
│   └── commands/
│       ├── discover.md                      # /discover
│       ├── qualify.md                       # /qualify
│       ├── analyze-site.md                  # /analyze-site <url>
│       ├── market-scan.md                   # /market-scan
│       └── full-pipeline.md                 # /full-pipeline <job>
│
├── queue/
│   ├── raw_jobs.json                        # unfiltered from discovery
│   ├── qualified_jobs.json                  # ACCEPT + HOLD
│   ├── rejected_jobs.json                   # filtered out
│   └── seen_ids.json                        # deduplication memory
│
├── jobs/
│   └── [JOB_ID]/
│       ├── raw_[JOB_ID].csv
│       ├── output_[JOB_ID].csv
│       ├── scraper_[JOB_ID].py
│       └── README_[JOB_ID].md
│
└── logs/
    └── discovery.log                        # cron log
```

---

## 🚀 First-Time VPS Setup (Do Once)

```bash
# 1. SSH into your Contabo VPS
ssh user@YOUR_VPS_IP

# 2. Clone or upload this project
git clone YOUR_REPO ~/freelance-system
# OR: scp -r freelance-system/ user@YOUR_VPS_IP:~/

# 3. Run the setup script
cd ~/freelance-system
chmod +x scripts/setup-vps.sh
bash scripts/setup-vps.sh

# 4. Set your Brave Search API key in opencode.json
nano opencode.json
# Replace: "YOUR_BRAVE_API_KEY_HERE" with your real key
# Get free key at: https://api.search.brave.com/

# 5. Activate Python environment
source ~/freelance-env/bin/activate

# 6. Test discovery
python scripts/run_pipeline.py full

# 7. Verify Chrome works with Playwright
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path='/usr/bin/google-chrome',
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page = b.new_page()
    page.goto('https://example.com')
    print('Chrome OK:', page.title())
    b.close()
"
```

---

## ⚡ Daily Workflow

### Step 1 — Discover Jobs
```bash
# Terminal
python scripts/run_pipeline.py full

# OR via OpenCode
/discover
```
Runs Upwork RSS + Freelancer API → qualifies all results → shows top 10.

### Step 2 — Review Top Jobs
```bash
python scripts/run_pipeline.py show
```
Displays a table of all ACCEPT jobs with complexity + suggested price.

### Step 3 — Analyze Target Site
When you pick a job and the client mentions (or you can infer) the target site:
```bash
# Terminal
python scripts/analyze_site.py https://target-site.com/products

# OR via OpenCode
/analyze-site https://target-site.com/products
```

This tells you **exactly which tool to use** (BS4 / Playwright / curl_cffi) and generates the OpenCode prompt to write the scraper.

### Step 4 — Run Full Pipeline
```
/full-pipeline
I need someone to scrape 500 products from https://shop.example.com into CSV.
Budget $100, need it in 24 hours. Python preferred.
```

Outputs: qualification + market check + offer + execution plan + ready-to-paste proposal.

### Step 5 — Write the Scraper
Copy the "OpenCode Starter Prompt" from the analyze_site output and paste it into a new OpenCode session. It will generate working code tuned to the specific site.

### Step 6 — Log and Deliver
```
/log-job won JOB001 $100
/log-job delivered JOB001
/log-job closed JOB001 "Great work, fast delivery" 5
```

---

## 📅 Weekly Schedule

| Day | Task | Command |
|-----|------|---------|
| Mon | Market intelligence refresh | `/market-scan` |
| Mon–Fri | Job discovery + qualify | `/discover` → `/qualify` |
| Daily | Process top 2–3 jobs | `/full-pipeline [listing]` |
| Daily | Site analysis on accepted jobs | `/analyze-site [url]` |
| Fri | Review tracker, lessons learned | Read `job-tracker.md` |

---

## 🔧 Scraping Tool Reference

### When to Use What

| Situation | Tool | Why |
|-----------|------|-----|
| Plain HTML page | `requests + BeautifulSoup` | Fastest, most stable |
| React/Vue/Angular site | `Playwright + Chrome` | Executes JS, uses VPS Chrome |
| Cloudflare protected | `curl_cffi` | Mimics Chrome TLS fingerprint |
| Basic JS challenge | `cloudscraper` | Lightweight CF bypass |
| Login-required | `Playwright` with cookies | Session persistence |
| Heavy bot protection (Akamai) | DECLINE or $300+ | Too risky for solo freelancer |

### VPS Chrome Configuration (copy into every Playwright script)
```python
browser = await p.chromium.launch(
    headless=True,
    executable_path="/usr/bin/google-chrome",
    args=[
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
    ]
)
```

### Install Commands (run once, already in setup-vps.sh)
```bash
pip install requests beautifulsoup4 lxml playwright scrapy
pip install cloudscraper curl_cffi fake-useragent pandas
playwright install chromium && playwright install-deps chromium
```

---

## 🧠 Strategy Decision Tree

```
Client posts job
        │
        ├── REJECT keywords found? → Skip
        │
        ├── No scraping keywords? → Skip
        │
        ├── Budget < $20? → Skip
        │
        ├── ACCEPT — run analyze_site.py on target
        │       │
        │       ├── complexity: low → BS4 → quote $50-$100
        │       │
        │       ├── complexity: medium → Playwright → quote $100-$200
        │       │
        │       ├── anti-bot: cloudflare → curl_cffi → quote $150-$250
        │       │
        │       └── complexity: very_high → HOLD / skip / quote $300+
        │
        └── Write proposal with sample → Submit within 24h
```

---

## 📊 VPS Resource Management

**Max concurrent scrapers by type:**
- BeautifulSoup: 8+ (very lightweight)
- Playwright/Chrome: 3 max (400MB/instance × 3 = 1.2GB)
- Scrapy: 4 (200MB each)

**If running multiple jobs simultaneously:**
```bash
# Check memory
free -h

# Check Chrome processes
ps aux | grep chrome

# Kill stuck Chrome instances
pkill -f google-chrome
```

---

## 🚨 Common Issues

### Chrome won't start on VPS
```bash
# Test it
google-chrome --headless --no-sandbox --dump-dom https://example.com 2>/dev/null | head -20

# If missing deps
sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2
```

### Upwork RSS returns empty
- Upwork occasionally changes their RSS URL structure
- Test manually: `curl "https://www.upwork.com/ab/feed/jobs/rss?q=web+scraping&sort=recency"`
- If empty, use Brave Search to find jobs via `/market-scan` and paste manually

### Freelancer API blocked
- They rate-limit aggressively; add `time.sleep(2)` between queries
- Or use Brave Search: `"site:freelancer.com web scraping python"`

### Site blocks even with curl_cffi
- Try: `session = cffi_requests.Session(impersonate="chrome124")`
- Or decline the job — protection levels above Cloudflare basic are not worth it for $100 gigs

---

Ready to start:
```bash
cd ~/freelance-system
source ~/freelance-env/bin/activate
python scripts/run_pipeline.py full
```
