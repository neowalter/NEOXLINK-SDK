---
name: neoxlink
description: >-
  UNSPSC-first B2B intent parsing and Agent Commerce via NEOXLINK MCP tools
  (neoxlink.parse_preview, neoxlink.confirmed_submit). Use when normalizing
  procurement or supply text to structured records, UNSPSC codes, or MCP-backed
  submit flows.
version: 0.6.0
metadata:
  openclaw:
    requires:
      env:
        - NEOXLINK_API_KEY
      bins:
        - neoxlink-mcp
    primaryEnv: NEOXLINK_API_KEY
    homepage: https://github.com/neowalter/NEOXLINK-SDK
    install:
      - kind: uv
        package: "neoxlink[mcp]==0.6.2"
        bins:
          - neoxlink-mcp
---

# NEOXLINK SDK (MCP)

Teach the agent to use **NEOXLINK** for **UNSPSC-aligned** structured previews and confirmed submits over **Model Context Protocol**, not ad-hoc JSON.

## Install

```bash
pip install 'neoxlink[mcp]==0.6.2'
# or: uv pip install 'neoxlink[mcp]==0.6.2'
```

Host env (set in MCP host / secret store; never commit):

- **NEOXLINK_API_KEY** — required for the cloud API.
- **NEOXLINK_BASE_URL** — optional; default `https://neoxailink.com`.
- **NEOXLINK_ENABLE_MATCH** — optional; set `1` to expose `neoxlink.match_intent` when the server is configured with a local matching engine.

Run stdio server: `neoxlink-mcp` (see `mcp-config.json` in this bundle).

## Tools

| Tool | When to use |
| --- | --- |
| `neoxlink.parse_preview` | NL → structured preview with UNSPSC when applicable; **no** auto-confirm. |
| `neoxlink.confirmed_submit` | Parse + confirm in one path → durable structured record. |
| `neoxlink.match_intent` | Only if `NEOXLINK_ENABLE_MATCH=1` and engine attached — ranked local match. |

## MCP resources

- `unspsc://catalog` — packaged UNSPSC subset as JSON.
- `unspsc://entry/{code}` — single 8-digit UNSPSC entry.

## Documentation

- [MCP integration](https://github.com/neowalter/NEOXLINK-SDK/blob/main/docs/wiki/mcp-integration.md)
- [UNSPSC quick ref](https://github.com/neowalter/NEOXLINK-SDK/blob/main/docs/wiki/unspsc-quick-ref.md)
- [OpenAPI](https://github.com/neowalter/NEOXLINK-SDK/blob/main/openapi.json)

## Example prompts

- Parse (preview only): buyer needs 500 recyclable corrugated cartons, delivery Shanghai in two weeks — return UNSPSC and structured preview, do not submit.
- Submit: confirmed sell-side supply for managed Kubernetes and 24/7 ops, side `supply`.
- List UNSPSC entries from `unspsc://catalog` relevant to “custom software development.”
