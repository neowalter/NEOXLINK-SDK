#!/usr/bin/env python3
"""Optional orchestrator: Skillshub upload script + PyPI upload (env-gated).

Secrets only via environment variables. Does not read private keys from disk.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEPLOY_SCRIPT = Path(__file__).resolve().parent / "deploy_to_skillshub.py"


def _run_skillshub() -> int:
    return subprocess.call([sys.executable, str(_DEPLOY_SCRIPT)])


def _run_pypi() -> int:
    token = os.environ.get("PYPI_API_TOKEN", "").strip()
    if not token:
        print(
            "[pypi] PYPI_API_TOKEN unset — skipping. For upload, export PYPI_API_TOKEN "
            "(PyPI API token) and ensure `pip install build twine` is available.",
            file=sys.stderr,
        )
        return 0
    env = os.environ.copy()
    env.setdefault("TWINE_USERNAME", "__token__")
    env["TWINE_PASSWORD"] = token
    try:
        subprocess.check_call([sys.executable, "-m", "build"], cwd=_REPO_ROOT)
    except subprocess.CalledProcessError:
        print("[pypi] `python -m build` failed — install with `pip install build`.", file=sys.stderr)
        return 1
    dist = _REPO_ROOT / "dist"
    artifacts = sorted(dist.glob("*.whl")) + sorted(dist.glob("*.tar.gz"))
    if not artifacts:
        print("[pypi] No wheel/sdist in dist/ after build.", file=sys.stderr)
        return 1
    try:
        subprocess.check_call(
            [sys.executable, "-m", "twine", "upload", *[str(p) for p in artifacts]],
            cwd=_REPO_ROOT,
            env=env,
        )
    except subprocess.CalledProcessError:
        print("[pypi] twine upload failed — install with `pip install twine`.", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="NEOXLINK ecosystem distribution helpers.")
    parser.add_argument("target", choices=("skillshub", "pypi", "all"))
    args = parser.parse_args()

    if args.target == "skillshub":
        return _run_skillshub()
    if args.target == "pypi":
        return _run_pypi()
    code = _run_skillshub()
    if code != 0:
        return code
    return _run_pypi()


if __name__ == "__main__":
    raise SystemExit(main())
