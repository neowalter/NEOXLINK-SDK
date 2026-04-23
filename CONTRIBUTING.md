# Contributing to neoxlink

Thanks for contributing.

**Before a PR, run (from repo root):**

```bash
pip install -e ".[dev]"
ruff check neoxlink_sdk tests
pytest
```

**Product scope:** contributions should strengthen **UNSPSC (Code + Name) + structured intent + Skill/MCP** — not a generic “chatbot wrapper” around the same APIs.

**Merge hygiene:** when a PR touches both documentation and `pyproject.toml` (dependencies or tooling), prefer small focused PRs or rebase in **docs → then tooling/deps** order to avoid repeated conflicts on `pyproject.toml`.

## Before you start, read

- `OPEN_SOURCE_SCOPE.md`
- `REPOSITORY_ARCHITECTURE.md`
- `CONTRIBUTOR_WORKFLOW.md`
- `DATA_COLLABORATION_GUIDELINES.md`
- `PROMPT_COLLABORATION.md`

## Quick start

1. Fork and clone the repository.
2. Create a feature branch.
3. Install locally:

```bash
pip install -e .
```

4. Run examples and compile checks before opening PR.

## Releasing to PyPI (GitHub Actions)

Releases use [pypa/gh-action-pypi-publish](https://github.com/marketplace/actions/pypi-publish) in `.github/workflows/publish-pypi.yml`: a **build** job produces `dist/`, then a **publish** job uploads to project [`neoxlink`](https://pypi.org/project/neoxlink/) using the **`PYPI_API_TOKEN`** secret. The workflow sets **`attestations: false`** so PyPI upload uses the token only (no OIDC); without that, the action can fail with missing `id-token: write` / OIDC errors.

**One-time setup**

1. GitHub → **Settings → Environments** → create **`pypi`** (optional: required reviewers, deployment branches).
2. Under that environment (or **Settings → Secrets and variables → Actions** at repo level), add **`PYPI_API_TOKEN`**: a [PyPI API token](https://pypi.org/manage/account/token/) with upload permission for **`neoxlink`**.
3. Optional later: switch to **Trusted Publishing** (OIDC) on PyPI for this repo + `publish-pypi.yml`, then remove the `with: password:` block from the workflow and grant the publish job `id-token: write` per the [action docs](https://github.com/marketplace/actions/pypi-publish).

**Cut a release**

1. Bump `version` in `pyproject.toml` and in `server.json` if you publish to the MCP Registry too.
2. Push a tag: `git tag vX.Y.Z && git push origin vX.Y.Z`, or run **Actions → Publish to PyPI → Run workflow**.

## Pull request guidelines

- Keep PRs focused and atomic.
- Include docs/examples for behavior changes.
- Preserve backward compatibility for public SDK APIs.
- Add migration notes when modifying signatures.

## Community velocity standards

- Label beginner-friendly tasks as `good-first-issue`.
- Maintainers should acknowledge new issues and PRs within 24-48 hours.
- Prefer small iterative reviews to keep contributor momentum high.

## What to contribute

- Model adapters
- Data source connectors
- Ranking strategies
- Evaluation scripts and benchmark data
- Documentation improvements
