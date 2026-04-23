# In-repo documentation (wiki mirror)

**Source of truth:** The canonical copy of UNSPSC, MCP, and **repository layout** handbooks for NEOXLINK-SDK lives in this `docs/wiki/` tree in the main repository so they are versioned with the code, reviewable in PRs, and linkable from `README.md`.

| Page | Content |
| --- | --- |
| [`unspsc-quick-ref.md`](unspsc-quick-ref.md) | UNSPSC usage / quick reference |
| [`mcp-integration.md`](mcp-integration.md) | MCP stdio server and tool surface |
| [`agent-channel-matrix.md`](agent-channel-matrix.md) | Agent interoperability matrix (MCP, OpenClaw, Hermes, Skillshub), checklists, uvx snippets |
| [`repository-layout.md`](repository-layout.md) | Top-level tree, HTTP vs catalog layers, `deprecated/` archival tree, how to run `pytest` on Python 3.11+ |

**GitHub Wiki (optional):** GitHub’s Wiki is a separate repository. If your project uses it, you can either:

- **Mirror** — periodically copy or sync these files into the Wiki (manual paste, a small script, or `gh` CLI with maintainer access), or  
- **Link only** — keep Wiki minimal and point readers to the files above on the default branch (recommended for a single source of truth).
