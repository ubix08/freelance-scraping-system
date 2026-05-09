#!/bin/bash
# =============================================================
# VPS Setup Script — AI Freelance Scraping System
# Contabo VPS: 4 core / 7GB RAM / Ubuntu 22.04
# =============================================================

set -e
echo "=== Installing system dependencies ==="
sudo apt-get update -y
sudo apt-get install -y \
  python3 python3-pip python3-venv \
  nodejs npm \
  curl wget git jq \
  xvfb \
  libnss3 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
  libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

echo "=== Setting up Python virtual environment ==="
cd ~
python3 -m venv freelance-env
source freelance-env/bin/activate

echo "=== Installing Python packages ==="
pip install --upgrade pip
pip install \
  requests \
  beautifulsoup4 \
  lxml \
  playwright \
  scrapy \
  selenium \
  pandas \
  openpyxl \
  fake-useragent \
  httpx \
  cloudscraper \
  curl-cffi \
  feedparser \
  schedule \
  python-dotenv \
  rich \
  typer

echo "=== Installing Playwright browsers ==="
# Use existing system Chrome if available, install Chromium as fallback
playwright install chromium
playwright install-deps chromium

echo "=== Installing Node.js packages ==="
npm install -g \
  @modelcontextprotocol/server-brave-search \
  playwright

echo "=== Verifying Chrome ==="
if command -v google-chrome &> /dev/null; then
  echo "✓ Google Chrome found: $(google-chrome --version)"
elif command -v chromium-browser &> /dev/null; then
  echo "✓ Chromium found: $(chromium-browser --version)"
else
  echo "Installing Chromium..."
  sudo apt-get install -y chromium-browser
fi

echo "=== Creating project directories ==="
mkdir -p ~/freelance-system/{jobs,queue,scripts,logs}
mkdir -p ~/freelance-system/.opencode/{context/freelance,commands}

echo ""
echo "=== Setup Complete ==="
echo "Activate env with: source ~/freelance-env/bin/activate"
echo "Python packages: requests, beautifulsoup4, playwright, scrapy, pandas, cloudscraper"
echo "Chrome: ready for Playwright automation"
