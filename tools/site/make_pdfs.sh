#!/usr/bin/env bash
# Print the report pages to PDF with headless Chrome. Run after tools/site/build.py.
# Usage: bash tools/site/make_pdfs.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
PORT=8791
python3 -I -m http.server "$PORT" >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER' EXIT
until curl -s -o /dev/null "http://localhost:$PORT/"; do sleep 0.2; done
for pair in "united-states:gds-report-united-states-2023" "global:gds-report-global-2023"; do
    slug=${pair%%:*}; file=${pair##*:}
    "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 \
        --print-to-pdf="reports/$file.pdf" "http://localhost:$PORT/reports/$slug/" 2>/dev/null
    echo "wrote reports/$file.pdf"
done
