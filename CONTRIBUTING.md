# Contributing to neoxlink-sdk

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
