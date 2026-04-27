# GitHub Wiki seed (copy-paste)

If you use the GitHub Wiki for end-user documentation, you can add pages from the content below. Replace vendor URLs with your canonical repository URL.

---

**Home**

# NEOXLINK-SDK

Python SDK: natural language → **machine-readable structured intent**, with **UNSPSC** for product/service classification where needed, plus **MCP** stdio server and Skill runtime. Connect agents to CRM, ERP, marketplaces, and custom backends—not only procurement. Core API: `NeoXlinkClient`, `StructuredSubmissionPipeline`, `NeoxlinkSkill`, `NeoxlinkMCPAdapter`. Install: `pip install neoxlink`. MCP: `pip install 'neoxlink[mcp]'` then `neoxlink-mcp` with `NEOXLINK_API_KEY` set. **Layout:** versioned wiki mirror under `docs/wiki/` (start with `repository-layout.md` for HTTP vs catalog vs orchestration). Historical non-shipping code lives in `deprecated/` only. See the repository [README](https://github.com/OWNER/REPO#readme) for examples.

---

**MCP**

# MCP integration

- Install: `pip install 'neoxlink[mcp]'`
- Run: `export NEOXLINK_API_KEY=...` then `neoxlink-mcp` (stdio).
- Optional: `NEOXLINK_ENABLE_MATCH=1` to register `neoxlink.match_intent` (in-memory default has no preloaded partners; use a custom `ProcurementIntentEngine` in your own deployment for production data).
- Config template: `mcp/config.neoxlink.example.json` in the repo; merge the `neoxlink` block into your host’s MCP JSON.

Tools exposed: `neoxlink.parse_preview`, `neoxlink.confirmed_submit`, and optionally `neoxlink.match_intent`.

---

**UNSPSC catalog**

# UNSPSC subset

The published subset is **one JSON file** shipped with the package: `neoxlink_sdk/data/unspsc_catalog.json`. The same data powers `neoxlink_sdk.unspsc` and `load_default_taxonomy_nodes()`. To extend the catalog, edit that file (and keep code + names consistent with [UNSPSC](https://www.unspsc.org/) governance for production use) and add regression tests under `tests/`.
