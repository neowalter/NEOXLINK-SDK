#!/usr/bin/env python3
"""Upload `skill-manifest.json` to a Skillshub-compatible HTTP endpoint.

Environment variables (never hard-code tokens in this file):
  SKILLSHUB_API_BASE     — required unless SKILLSHUB_DRY_RUN=1 (e.g. https://api.skillshub.example)
  SKILLSHUB_API_TOKEN    — bearer token; required when not dry-run
  SKILLSHUB_UPLOAD_PATH  — optional, default /v1/skills
  SKILLSHUB_DRY_RUN      — set to 1 to print payload and skip HTTP

The live skillshub.ai contract may differ; treat paths and fields as templates and adjust
to the vendor OpenAPI.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx


def _manifest_path() -> Path:
    return Path(__file__).resolve().parent / "skill-manifest.json"


def main() -> int:
    dry = os.environ.get("SKILLSHUB_DRY_RUN", "").strip().lower() in ("1", "true", "yes")
    base = os.environ.get("SKILLSHUB_API_BASE", "").rstrip("/")
    token = os.environ.get("SKILLSHUB_API_TOKEN", "")
    path = os.environ.get("SKILLSHUB_UPLOAD_PATH", "/v1/skills")
    manifest = json.loads(_manifest_path().read_text(encoding="utf-8"))

    if dry:
        print("[skillshub] DRY_RUN: would POST the following manifest:", file=sys.stderr)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0

    if not base:
        print("SKILLSHUB_API_BASE is required (or set SKILLSHUB_DRY_RUN=1).", file=sys.stderr)
        return 1
    if not token:
        print("SKILLSHUB_API_TOKEN is required when not in DRY_RUN.", file=sys.stderr)
        return 1

    url = f"{base}{path if path.startswith('/') else '/' + path}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print(f"[skillshub] POST {url}", file=sys.stderr)
    response = httpx.post(url, headers=headers, json=manifest, timeout=60.0)
    print(response.text)
    response.raise_for_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
