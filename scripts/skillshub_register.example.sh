#!/usr/bin/env bash
# Example one-shot registration for agents.skills (SkillHub) style runtimes.
# Replace ENDPOINT, PROJECT, and path to your local SKILL.md or bundle zip.
# skillshub.ai and similar registries have different APIs: treat this as a template.
set -euo pipefail
ENDPOINT="${SKILLHUB_API_URL:-https://api.example.com/v1/skills}"
echo "POST $ENDPOINT (placeholder — replace with real registry curl)"
# curl -sS -X POST "$ENDPOINT" \
#   -H "Authorization: Bearer $SKILLHUB_TOKEN" \
#   -F "name=neoxlink-procurement" \
#   -F "bundle=@./neoxlink-skill.zip"
echo "Ship a directory containing: SKILL.md (see examples/02_skill_runtime.py), and optional mcp/ config to pair MCP + skills."
