# NEOXLINK-SDK Public Repository Workspace

This folder is for the open-source core datastore + matching + SDK repository.

## Target repository

- GitHub owner: `neowalter`
- Suggested repo: `NEOXLINK-SDK`
- Suggested remote: `git@github.com:neowalter/NEOXLINK-SDK.git`

## Initial setup

1. Enter this folder:
   - `cd workspaces/neoxlink-sdk-public`
2. Clone public repo:
   - `git clone git@github.com:neowalter/NEOXLINK-SDK.git .`
3. Install local dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -e .`

## What should live here

- `libs/core` style contracts and dedup/matching utilities
- language SDKs (Python/TS)
- public docs and examples

## Sync flow from private repo

- From private repo root, use:
  - `./scripts/sync_public_core.sh /absolute/path/to/workspaces/neoxlink-sdk-public`
- Review diff, commit, and push to public repo.
