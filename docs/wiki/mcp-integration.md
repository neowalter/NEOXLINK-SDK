# MCP integration guide

NEOXLINK-SDK exposes a **Model Context Protocol (MCP)** stdio server and a Python `NeoxlinkMCPAdapter` so agents can call **stable tool names** instead of ad-hoc prompts — aligned with **UNSPSC and structured submit**, not generic chit-chat.

## Install

```bash
pip install 'neoxlink-sdk[mcp]'
```

The optional `mcp` extra pins the **`mcp`** and **`anyio`** libraries required for the stdio server; see `pyproject.toml` (`[project.optional-dependencies] mcp`).

## stdio server (`neoxlink-mcp`)

```bash
export NEOXLINK_API_KEY=your_key
neoxlink-mcp
```

- Optional: `NEOXLINK_BASE_URL` — API base (default in code).  
- Optional: `NEOXLINK_ENABLE_MATCH=1` — registers `neoxlink.match_intent` when a local `ProcurementIntentEngine` is configured in `mcp_server.py`.

Host configuration: see [`mcp/config.neoxlink.example.json`](../../mcp/config.neoxlink.example.json) in the repository root (path relative to your checkout).

## Tool surface (names are stable)

| Tool | Purpose |
| --- | --- |
| `neoxlink.parse_preview` | Parse NL → structured preview (UNSPSC in preview when available); no auto-confirm. |
| `neoxlink.confirmed_submit` | Parse + confirm in one call → structured record. |
| `neoxlink.match_intent` | Only when an engine is attached — staged match / rank. |

Implementation reference: `neoxlink_sdk/mcp.py` (`NeoxlinkMCPAdapter`), `neoxlink_sdk/mcp_server.py` (FastMCP-style wiring).

## Compatibility and upgrades

- **Pin versions** in production using the same `mcp` range as the SDK’s optional extra; after upgrading `mcp` on the host, run the test suite: `pytest tests/test_mcp_adapter.py tests/test_mcp_server_module.py -q`.  
- **Spec drift:** Follow [modelcontextprotocol.io](https://modelcontextprotocol.io/) for transport and capability changes; adapter changes belong in `neoxlink_sdk/mcp_server.py` / `mcp.py`.

## In-process (Python) use

To embed the adapter without stdio, construct `NeoxlinkMCPAdapter(NeoxlinkSkill(...), engine=...)` and call `list_tools` / `call_tool` as in `tests/test_mcp_adapter.py`.
