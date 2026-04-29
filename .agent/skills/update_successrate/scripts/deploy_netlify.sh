#!/bin/bash
# Deploy all HTML files to Netlify (idrchargechart site)
# Usage: bash deploy_netlify.sh
#
# Prerequisites:
#   - Netlify personal access token stored in NETLIFY_TOKEN env var
#     or defaulting to the project token below
#   - curl installed

set -euo pipefail

BASE="/Users/mac/ws/tools/successrate"
SITE_ID="bf7e3d36-3b33-45c2-a7db-712231ba0895"
NETLIFY_TOKEN="${NETLIFY_TOKEN:-nfp_H5TSbCwBma1XjFAGNUkw3ikrk2cmAJhj90be}"
DEPLOY_DIR=$(mktemp -d)

echo "📦 Preparing deployment..."

# Copy all HTML files to temp deploy dir
cp "$BASE/index.html" \
   "$BASE/idr_charge_chart.html" \
   "$BASE/bdt_charge_chart.html" \
   "$BASE/brl_charge_chart.html" \
   "$BASE/php_charge_chart.html" \
   "$DEPLOY_DIR/"

echo "  Files copied to $DEPLOY_DIR:"
ls -la "$DEPLOY_DIR/"

# Create zip
ZIP_FILE=$(mktemp).zip
(cd "$DEPLOY_DIR" && zip -r "$ZIP_FILE" .)

echo ""
echo "🚀 Deploying to Netlify..."

RESPONSE=$(curl -s -X POST \
  "https://api.netlify.com/api/v1/sites/${SITE_ID}/deploys" \
  -H "Authorization: Bearer ${NETLIFY_TOKEN}" \
  -H "Content-Type: application/zip" \
  --data-binary "@${ZIP_FILE}")

DEPLOY_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
STATE=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('state',''))" 2>/dev/null || echo "")
URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ssl_url','') or json.load(sys.stdin).get('url',''))" 2>/dev/null || echo "")

# Cleanup
rm -rf "$DEPLOY_DIR" "$ZIP_FILE"

if [ -n "$DEPLOY_ID" ] && [ "$STATE" = "uploaded" ]; then
    echo ""
    echo "✅ Deploy successful!"
    echo "  Deploy ID: $DEPLOY_ID"
    echo "  State:     $STATE"
    echo "  URL:       $URL"
    echo ""
    echo "📊 Pages:"
    echo "  首页导航:   ${URL}/"
    echo "  IDR Charge: ${URL}/idr_charge_chart"
    echo "  BDT Charge: ${URL}/bdt_charge_chart"
    echo "  BRL Charge: ${URL}/brl_charge_chart"
    echo "  PHP Charge: ${URL}/php_charge_chart"
else
    echo ""
    echo "❌ Deploy failed!"
    echo "  Response: $RESPONSE"
    exit 1
fi
