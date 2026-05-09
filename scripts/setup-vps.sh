#!/usr/bin/env bash
set -euo pipefail

echo "=== Layer 1 — VPS Setup ==="

sudo apt-get update
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    git curl \
    chromium-browser chromium-chromedriver \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2

python3 -m venv ~/freelance-env
source ~/freelance-env/bin/activate

pip install --upgrade pip
pip install requests beautifulsoup4 lxml playwright feedparser
playwright install chromium
playwright install-deps chromium

echo "Verify Chrome:"
google-chrome --headless --no-sandbox \
    --dump-dom https://example.com 2>/dev/null | head -3

echo "=== Done. Activate: source ~/freelance-env/bin/activate ==="
