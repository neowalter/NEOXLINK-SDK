#!/usr/bin/env bash
# Publish a minimal NEOXLINK / MCP skill manifest to a skillshub-style HTTP endpoint.
# Requires SKILLSHUB_API_BASE and SKILLSHUB_API_TOKEN unless SKILLSHUB_DRY_RUN=1.
set -euo pipefail

API_BASE="${SKILLSHUB_API_BASE:-}"
TOKEN="${SKILLSHUB_API_TOKEN:-}"
DRY="${SKILLSHUB_DRY_RUN:-0}"
ENDPOINT_PATH="${SKILLSHUB_UPLOAD_PATH:-/v1/skills}"

if [[ -z "$API_BASE" && "$DRY" != "1" ]]; then
  echo "SKILLSHUB_API_BASE is required (or set SKILLSHUB_DRY_RUN=1)." >&2
  exit 1
fi

PAYLOAD='{
  "name": "neoxlink-mcp",
  "version": "0.6.2",
  "summary": "UNSPSC-first structured intent + MCP tools (neoxlink.parse_preview, neoxlink.confirmed_submit).",
  "mcp": {
    "server_command": "neoxlink-mcp",
    "tools": [
      "neoxlink.parse_preview",
      "neoxlink.confirmed_submit"
    ]
  },
  "docs": {
    "readme": "https://github.com/neowalter/NEOXLINK-SDK/blob/main/README.md",
    "mcp": "https://github.com/neowalter/NEOXLINK-SDK/blob/main/docs/wiki/mcp-integration.md"
  }
}'

if [[ "$DRY" == "1" ]]; then
  echo "[skillshub] DRY_RUN=1 — payload:"
  echo "$PAYLOAD" | python3 -m json.tool
  echo "[skillshub] No request sent."
  exit 0
fi

if [[ -z "$TOKEN" ]]; then
  echo "SKILLSHUB_API_TOKEN is required when not in DRY_RUN." >&2
  exit 1
fi

URL="${API_BASE%/}${ENDPOINT_PATH}"
echo "[skillshub] POST $URL" >&2

curl -sS -X POST "$URL" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"

echo
echo "[skillshub] done."
