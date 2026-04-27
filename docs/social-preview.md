# Social preview and SEO (GitHub)

- **Repository topics**: on GitHub **About**, add at least: `mcp`, `model-context-protocol`, `unspsc`, `structured-intent`, `system-integration`, `python`, `llm`, `agent-sdk`, `neoxlink`.
- **Open Graph / Twitter image**: in the repo’s **Settings → General → Social preview**, upload a 1280×640 (or 1200×600) image that includes the product name, tagline (e.g. *Chat to Transaction*), and the UNSPSC + MCP angle. GitHub will serve this as `og:image` for links to the default branch.
- **Description**: a single sentence for **About** that matches the PyPI description: natural language to machine-readable structured intent, UNSPSC normalization, MCP tools, and integration with existing business systems.

The `[project]` metadata in `pyproject.toml` includes `keywords` and `[project.urls]` to improve package-index and search discoverability; keep them aligned with the README tagline when you rebrand.
