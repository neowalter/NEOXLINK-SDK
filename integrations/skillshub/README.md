# skillshub.ai integration (optional)

This directory holds a **publishing script** for registries that accept HTTP uploads of skill metadata. NEOXLINK-SDK is **not** a generic chatbot: scripts here must describe **UNSPSC-aligned / MCP** surfaces only.

## Prerequisites

- `SKILLSHUB_API_BASE` — base URL (e.g. `https://api.example.com`); required.
- `SKILLSHUB_API_TOKEN` — bearer token; required for authenticated uploads.
- `SKILLSHUB_DRY_RUN=1` — log the payload and exit `0` without a network call (safe default for CI).

> **Note:** The real skillshub.ai API shape may differ. Treat `publish.sh` as a **template**: adjust paths and JSON fields to match the vendor’s current OpenAPI or dashboard export.

## Usage

```bash
export SKILLSHUB_API_BASE="https://api.skillshub.example"
export SKILLSHUB_API_TOKEN="…"
./integrations/skillshub/publish.sh
# or
SKILLSHUB_DRY_RUN=1 ./integrations/skillshub/publish.sh
```

## What gets published (stub)

A minimal document referencing stable MCP tool names `neoxlink.parse_preview` and `neoxlink.confirmed_submit`. Expand with your `README` and `docs/wiki` links before production use.
