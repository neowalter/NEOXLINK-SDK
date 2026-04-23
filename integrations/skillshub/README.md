# skillshub.ai integration (optional)

Artifacts for registries that accept skill metadata and MCP runtime descriptors. NEOXLINK-SDK focuses on **UNSPSC Standardization**, **B2B**, and **Agent Commerce** — not generic chat.

## Files

| File | Purpose |
| --- | --- |
| `skill-manifest.json` | Vendor-oriented manifest (tools, resources, env, store copy, OpenAPI pointer). |
| `deploy_to_skillshub.py` | `POST` manifest to `SKILLSHUB_API_BASE` + `SKILLSHUB_UPLOAD_PATH`. |
| `ecosystem_deploy.py` | Optional orchestrator: Skillshub script + PyPI upload when `PYPI_API_TOKEN` is set. |

## Environment variables

**Skillshub upload**

- `SKILLSHUB_API_BASE` — required unless `SKILLSHUB_DRY_RUN=1`
- `SKILLSHUB_API_TOKEN` — bearer token when not dry-run
- `SKILLSHUB_UPLOAD_PATH` — optional, default `/v1/skills`
- `SKILLSHUB_DRY_RUN=1` — print JSON and skip HTTP

**PyPI (optional, via `ecosystem_deploy.py pypi|all`)**

- `PYPI_API_TOKEN` — PyPI API token; script sets `TWINE_USERNAME=__token__` and `TWINE_PASSWORD` from it
- Requires `pip install build twine`

## Usage

```bash
# Dry-run (safe)
SKILLSHUB_DRY_RUN=1 python integrations/skillshub/deploy_to_skillshub.py

# Upload (replace base URL with the vendor’s current endpoint)
export SKILLSHUB_API_BASE="https://api.skillshub.example"
export SKILLSHUB_API_TOKEN="…"
python integrations/skillshub/deploy_to_skillshub.py

# Optional: Skillshub + PyPI
export PYPI_API_TOKEN="…"
python integrations/skillshub/ecosystem_deploy.py all
```

The real **skillshub.ai** API may differ; adjust paths and JSON fields to match their OpenAPI or dashboard.

Legacy shell helper: `./integrations/skillshub/publish.sh`.
