#!/usr/bin/env bash
set -euo pipefail

URL="${1:-http://localhost:8765/menu/}"
OUT="${2:-/tmp/chowdown-lighthouse.json}"
LH_DIR="/tmp/lh"
NPM_CACHE="/tmp/npm-cache-codex"

mkdir -p "$LH_DIR" "$NPM_CACHE"
npm --prefix "$LH_DIR" --cache "$NPM_CACHE" install lighthouse@latest >/tmp/lh-install.log 2>&1

CHROME_PATH="${CHROME_PATH:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}" \
"$LH_DIR/node_modules/.bin/lighthouse" "$URL" \
  --quiet \
  --chrome-flags="--headless=new --no-sandbox --disable-gpu --user-data-dir=/tmp/lh-chrome-profile-$$" \
  --form-factor=mobile \
  --screenEmulation.mobile \
  --output=json \
  --output-path="$OUT"

node -e "const r=require('$OUT'); console.log(Object.fromEntries(Object.entries(r.categories).map(([k,v])=>[k,Math.round(v.score*100)]))); for (const [id,a] of Object.entries(r.audits)) { if (typeof a.score==='number' && a.score<1 && !['notApplicable','informative','manual'].includes(a.scoreDisplayMode)) console.log(id, a.score, a.title, a.displayValue||''); }"
