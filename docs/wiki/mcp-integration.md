# MCP integration guide

NEOXLINK-SDK exposes a **Model Context Protocol (MCP)** stdio server and a Python `NeoxlinkMCPAdapter` so agents can call **stable tool names** instead of ad-hoc prompts — aligned with **UNSPSC and structured submit**, not generic chit-chat.

## MCP Registry (PyPI / preview)

The official flow is documented in the [Registry quickstart](https://modelcontextprotocol.io/registry/quickstart) and [supported package types](https://modelcontextprotocol.io/registry/package-types). This project ships as a **PyPI** package (`neoxlink`), not npm.

**Ownership check (PyPI):** the project `README.md` on PyPI must contain an HTML comment whose value matches `server.json`:

`<!-- mcp-name: io.github.neowalter/neoxlink -->`

**Steps (summary):**

1. Bump and publish **`neoxlink`** to [PyPI](https://pypi.org/project/neoxlink/) so the version in `server.json` matches **`pyproject.toml`** and the published wheel/sdist (`python -m build` + `twine upload`, or your CI). Install for MCP is `pip install 'neoxlink[mcp]'`; the console script is **`neoxlink-mcp`**.
2. Install the publisher CLI (`mcp-publisher`) per the quickstart.
3. From the repository root, run `mcp-publisher login github` (server name uses the `io.github.neowalter/` prefix so it matches GitHub authentication).
4. Run `mcp-publisher publish` with the checked-in `server.json`.

The Registry is in **preview**; expect possible breaking changes ([registry issues](https://github.com/modelcontextprotocol/registry/issues)).

## Install

```bash
pip install 'neoxlink[mcp]'
```

The optional `mcp` extra pins the **`mcp`** and **`anyio`** libraries required for the stdio server; see `pyproject.toml` (`[project.optional-dependencies] mcp`).

## stdio server (`neoxlink-mcp`)

```bash
export NEOXLINK_API_KEY=your_key
neoxlink-mcp
```

- Optional: `NEOXLINK_BASE_URL` — API base (default in code).  
- Optional: `NEOXLINK_ENABLE_MATCH=1` — registers `neoxlink.match_intent` when a local `ProcurementIntentEngine` is configured in `mcp_server.py`.

Host configuration:

- Root template: [`mcp-config.json`](../../mcp-config.json) — copy into your MCP host (Claude Desktop / Cursor) and **set `NEOXLINK_API_KEY` in the host UI or secret store** (do not commit secrets).
- Alternate example: [`mcp/config.neoxlink.example.json`](../../mcp/config.neoxlink.example.json).

## Tool surface (names are stable)

| Tool | Purpose |
| --- | --- |
| `neoxlink.parse_preview` | Parse NL → structured preview (UNSPSC in preview when available); no auto-confirm. |
| `neoxlink.confirmed_submit` | Parse + confirm in one call → structured record. |
| `neoxlink.match_intent` | Only when an engine is attached — staged match / rank. |

## MCP resources (UNSPSC packaged subset)

The stdio server advertises:

- **`unspsc://catalog`** — full JSON array shipped in `neoxlink_sdk/data/unspsc_catalog.json` (Standardization / offline lookup).
- **`unspsc://entry/{code}`** — one 8-digit UNSPSC record from that subset (URI template).

Implementation reference: `neoxlink_sdk/mcp.py` (`NeoxlinkMCPAdapter`), `neoxlink_sdk/mcp_server.py` (low-level `mcp.server.Server` handlers).

## Compatibility and upgrades

- **Pin versions** in production using the same `mcp` range as the SDK’s optional extra; after upgrading `mcp` on the host, run the test suite: `pytest tests/test_mcp_adapter.py tests/test_mcp_server_module.py -q`.  
- **Spec drift:** Follow [modelcontextprotocol.io](https://modelcontextprotocol.io/) for transport and capability changes; adapter changes belong in `neoxlink_sdk/mcp_server.py` / `mcp.py`.

## In-process (Python) use

To embed the adapter without stdio, construct `NeoxlinkMCPAdapter(NeoxlinkSkill(...), engine=...)` and call `list_tools` / `call_tool` as in `tests/test_mcp_adapter.py`.
