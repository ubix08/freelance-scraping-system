#!/usr/bin/env python3
"""
Site Analyzer — Agent 4 Core Tool
Given a URL, determines scraping strategy, complexity, and generates starter code.
Called by OpenCode during job analysis.

Usage:
    python analyze_site.py <url>
    python analyze_site.py https://example.com/products
"""

import sys
import json
import time
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()

# ─── DETECTION PATTERNS ───────────────────────────────────────────────────────

CLOUDFLARE_SIGNALS = [
    "cloudflare", "cf-ray", "__cfduid", "__cf_bm",
    "Checking your browser", "DDoS protection",
    "cf_clearance", "403 Forbidden",
]

CAPTCHA_SIGNALS = [
    "recaptcha", "hcaptcha", "captcha", "challenge",
    "robot", "are you human", "verify you are",
]

JS_SIGNALS = [
    "window.__NEXT_DATA__", "__NUXT__", "ng-app",
    "react-root", "vue-app", "__REDUX__",
    "text/javascript", "application/json",
    "Loading...", "Please enable JavaScript",
]

PAGINATION_PATTERNS = {
    "query_page":     ["?page=", "?p=", "&page=", "&p=", "?offset="],
    "path_segment":   ["/page/", "/p/", "/pg/"],
    "load_more":      ["load more", "show more", "load_more"],
    "infinite_scroll":["infinite", "scroll", "IntersectionObserver"],
    "numbered_links": ["pagination", "pager", "paginate"],
}

ANTI_BOT_TOOLS = {
    "cloudflare":   ["cf-ray", "__cf_bm", "cloudflare"],
    "datadome":     ["datadome", "dd_"],
    "akamai":       ["akamai", "_abck", "bm_sv"],
    "imperva":      ["imperva", "incapsula", "visid_incap"],
    "distil":       ["distil"],
    "perimeterx":   ["perimeterx", "_pxvid"],
}

# ─── ANALYSIS FUNCTIONS ───────────────────────────────────────────────────────

def fetch_page(url: str) -> tuple[requests.Response | None, bool]:
    """Fetch page with realistic browser headers. Returns (response, is_dynamic)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xhtml+xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        html = resp.text.lower()
        is_dynamic = any(sig.lower() in html for sig in JS_SIGNALS)
        return resp, is_dynamic
    except requests.exceptions.ConnectionError:
        return None, False
    except Exception:
        return None, False


def detect_anti_bot(response: requests.Response) -> dict:
    """Detect anti-bot systems from headers and body."""
    headers_str = str(response.headers).lower()
    body_lower  = response.text.lower()
    combined    = headers_str + body_lower

    detected = []
    for name, signals in ANTI_BOT_TOOLS.items():
        if any(sig in combined for sig in signals):
            detected.append(name)

    has_captcha = any(sig in body_lower for sig in CAPTCHA_SIGNALS)
    status = response.status_code

    if not detected and status == 200:
        level = "none"
    elif status in [403, 429, 503] or detected:
        level = "heavy" if detected else "moderate"
    elif has_captcha:
        level = "heavy"
    else:
        level = "low"

    return {
        "level": level,
        "systems_detected": detected,
        "has_captcha": has_captcha,
        "status_code": status,
    }


def detect_pagination(soup: BeautifulSoup, html: str) -> dict:
    """Detect pagination type from parsed HTML."""
    html_lower = html.lower()
    results = {}

    for ptype, patterns in PAGINATION_PATTERNS.items():
        found = any(p in html_lower for p in patterns)
        if found:
            results[ptype] = True

    # Look for next page links
    next_links = soup.find_all("a", string=lambda t: t and "next" in t.lower())
    if next_links:
        results["next_link_found"] = next_links[0].get("href", "")

    if not results:
        results["type"] = "single_page_or_unknown"

    return results


def extract_data_selectors(soup: BeautifulSoup) -> dict:
    """Try to identify likely data container selectors."""
    suggestions = {}

    # Product/item cards
    for cls in ["product", "item", "card", "listing", "result", "entry", "row"]:
        elements = soup.find_all(class_=lambda c: c and cls in c.lower() if c else False)
        if len(elements) >= 3:
            suggestions["item_container"] = f".{elements[0].get('class', [cls])[0]}"
            break

    # Price fields
    for cls in ["price", "cost", "amount", "rate"]:
        els = soup.find_all(class_=lambda c: c and cls in c.lower() if c else False)
        if els:
            suggestions["price_field"] = f".{els[0].get('class', [cls])[0]}"
            break

    # Title fields
    for tag in ["h2", "h3", "h4"]:
        els = soup.find_all(tag)
        if len(els) >= 3:
            suggestions["title_field"] = tag
            break

    return suggestions


def recommend_strategy(is_dynamic: bool, anti_bot: dict, pagination: dict) -> dict:
    """Select the best scraping tool and configuration."""
    level = anti_bot["level"]
    systems = anti_bot["systems_detected"]

    if "cloudflare" in systems or "datadome" in systems:
        tool = "curl_cffi"
        approach = "curl_cffi with browser impersonation (bypasses Cloudflare TLS fingerprinting)"
        code_template = "curl_cffi"
    elif is_dynamic and level in ["none", "low"]:
        tool = "playwright"
        approach = "Playwright + Chromium headless (local Chrome on VPS)"
        code_template = "playwright"
    elif level == "none" and not is_dynamic:
        tool = "beautifulsoup"
        approach = "requests + BeautifulSoup (fastest, most stable)"
        code_template = "beautifulsoup"
    elif level == "moderate":
        tool = "cloudscraper"
        approach = "cloudscraper (handles basic JS challenges + TLS)"
        code_template = "cloudscraper"
    else:
        tool = "playwright_stealth"
        approach = "Playwright with stealth plugin + undetected-chromium"
        code_template = "playwright"

    # Pagination config
    ptype = list(pagination.keys())[0] if pagination else "unknown"

    complexity = "low"
    if is_dynamic:
        complexity = "medium"
    if level in ["moderate", "heavy"]:
        complexity = "high"
    if "cloudflare" in systems or "datadome" in systems:
        complexity = "very_high"

    return {
        "primary_tool": tool,
        "approach": approach,
        "code_template": code_template,
        "pagination_type": ptype,
        "complexity": complexity,
        "feasibility": "yes" if complexity != "very_high" else "risky",
        "estimated_dev_hours": {"low": 2, "medium": 4, "high": 8, "very_high": 12}[complexity],
    }


def generate_starter_prompt(url: str, strategy: dict, selectors: dict) -> str:
    """Generate the OpenCode prompt to write the scraper."""
    tool = strategy["code_template"]
    pagination = strategy["pagination_type"]

    if tool == "beautifulsoup":
        return f"""Write a Python web scraper using requests + BeautifulSoup for:
URL: {url}

Extract data using these likely selectors:
{json.dumps(selectors, indent=2)}

Requirements:
- Pagination: {pagination} — handle all pages
- Add 1.5–3s random delay between requests
- Use realistic User-Agent header
- Handle missing fields gracefully (empty string, don't crash)
- Export to: output.csv
- Print progress every 10 rows
- Wrap in main() function"""

    elif tool == "playwright":
        return f"""Write a Python Playwright scraper using async Playwright + Chromium for:
URL: {url}

Setup for VPS (headless, no sandbox):
  browser = await p.chromium.launch(
    headless=True,
    executable_path="/usr/bin/google-chrome",  # use local Chrome
    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
  )

Extract data using these likely selectors:
{json.dumps(selectors, indent=2)}

Requirements:
- Pagination: {pagination}
- Wait for network idle before extracting
- Random delay 1.5–3s between pages
- Export to: output.csv"""

    elif tool == "curl_cffi":
        return f"""Write a Python scraper using curl_cffi to bypass Cloudflare for:
URL: {url}

from curl_cffi import requests as cffi_requests
session = cffi_requests.Session(impersonate="chrome120")
resp = session.get(url, headers={{...}})

Extract: {json.dumps(selectors, indent=2)}
Requirements:
- Handle Cloudflare challenge (automatic with curl_cffi)
- Pagination: {pagination}
- Export to: output.csv"""

    return f"Write a scraper for {url} using {tool}. Extract: {json.dumps(selectors)}. Paginate: {pagination}."


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def analyze(url: str) -> dict:
    console.print(f"\n[bold cyan]🔬 Analyzing: {url}[/bold cyan]")
    domain = urlparse(url).netloc

    # Fetch
    console.print("  [dim]Fetching page...[/dim]")
    resp, is_dynamic = fetch_page(url)

    if resp is None:
        return {"error": "Could not fetch URL — may require login or VPN"}

    soup = BeautifulSoup(resp.text, "lxml")

    # Analyze
    anti_bot    = detect_anti_bot(resp)
    pagination  = detect_pagination(soup, resp.text)
    selectors   = extract_data_selectors(soup)
    strategy    = recommend_strategy(is_dynamic, anti_bot, pagination)
    prompt      = generate_starter_prompt(url, strategy, selectors)

    result = {
        "url": url,
        "domain": domain,
        "status_code": resp.status_code,
        "is_javascript_rendered": is_dynamic,
        "anti_bot": anti_bot,
        "pagination": pagination,
        "detected_selectors": selectors,
        "strategy": strategy,
        "opencode_prompt": prompt,
        "analyzed_at": time.strftime("%Y-%m-%d %H:%M UTC"),
    }

    # Pretty output
    table = Table(title=f"Site Analysis — {domain}")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Status",        str(resp.status_code))
    table.add_row("JS Rendered",   "⚠ YES" if is_dynamic else "✓ Static")
    table.add_row("Anti-Bot",      f"[red]{anti_bot['level']}[/red]" if anti_bot["level"] != "none" else "✓ None")
    table.add_row("Systems",       ", ".join(anti_bot["systems_detected"]) or "none")
    table.add_row("Pagination",    list(pagination.keys())[0] if pagination else "single page")
    table.add_row("Recommended",   f"[bold green]{strategy['primary_tool']}[/bold green]")
    table.add_row("Complexity",    strategy["complexity"])
    table.add_row("Feasibility",   f"[green]{strategy['feasibility']}[/green]" if strategy["feasibility"] == "yes" else f"[red]{strategy['feasibility']}[/red]")
    table.add_row("Est. Dev Hours",str(strategy["estimated_dev_hours"]))
    console.print(table)

    console.print(Panel(prompt, title="[bold]OpenCode Starter Prompt[/bold]", border_style="green"))

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]Usage: python analyze_site.py <url>[/red]")
        sys.exit(1)

    result = analyze(sys.argv[1])
    output_path = f"/tmp/site_analysis_{urlparse(sys.argv[1]).netloc.replace('.','_')}.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    console.print(f"\n[dim]Full report saved: {output_path}[/dim]")
