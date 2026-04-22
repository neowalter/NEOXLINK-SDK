"""Single source of truth for the packaged UNSPSC subset (code + name + keywords)."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(frozen=True)
class UNSPSCEntry:
    code: str
    name: str
    keywords: tuple[str, ...]


def default_unspsc_catalog_path() -> Path:
    """Path to the packaged JSON (for `TaxonomyLoader` and file-based tools)."""
    return Path(__file__).resolve().parent / "data" / "unspsc_catalog.json"


def load_unspsc_entries_from_path(path: Path) -> tuple[UNSPSCEntry, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return _rows_to_entries(data)


def load_unspsc_entries_from_bytes(raw: bytes) -> tuple[UNSPSCEntry, ...]:
    data = json.loads(raw.decode("utf-8"))
    return _rows_to_entries(data)


def _rows_to_entries(data: list[dict]) -> tuple[UNSPSCEntry, ...]:
    out: list[UNSPSCEntry] = []
    for item in data:
        kws = item.get("keywords") or []
        out.append(
            UNSPSCEntry(
                code=str(item["code"]),
                name=str(item["name"]),
                keywords=tuple(str(k) for k in kws),
            )
        )
    return tuple(out)


def load_unspsc_entries() -> tuple[UNSPSCEntry, ...]:
    """Load the default packaged UNSPSC catalog."""
    return load_unspsc_entries_from_path(default_unspsc_catalog_path())


def keyword_idf(catalog: tuple[UNSPSCEntry, ...]) -> dict[str, float]:
    """Inverse document frequency by keyword (higher = more discriminating in this small catalog)."""
    n = max(1, len(catalog))
    df: dict[str, int] = {}
    for entry in catalog:
        for kw in set(entry.keywords):
            df[kw] = df.get(kw, 0) + 1
    return {k: math.log(1.0 + (n - c + 0.5) / (c + 0.5)) for k, c in df.items()}


# Loaded once; tests can patch `load_unspsc_entries` by re-importing if needed, or pass paths in helpers.
CATALOG: Final[tuple[UNSPSCEntry, ...]] = load_unspsc_entries()
KEYWORD_IDF: Final[dict[str, float]] = keyword_idf(CATALOG)
