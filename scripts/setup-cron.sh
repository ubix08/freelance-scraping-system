#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$HOME/freelance-system"
ENV_DIR="$HOME/freelance-env"

echo "=== Installing daily cron jobs ==="

cron_jobs=(
    "0 8 * * 1-5 cd $PROJECT_DIR && $ENV_DIR/bin/python scripts/market_research.py >> logs/market_research.log 2>&1"
    "0 14 * * 1-5 cd $PROJECT_DIR && $ENV_DIR/bin/python scripts/market_research.py >> logs/market_research.log 2>&1"
)

(crontab -l 2>/dev/null || true; printf "%s\n" "${cron_jobs[@]}") | crontab -

echo "Cron installed:"
echo "  Mon-Fri 8:00 AM — market research scan"
echo "  Mon-Fri 2:00 PM — market research scan"
echo ""
echo "Verify with: crontab -l"
