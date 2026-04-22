from __future__ import annotations

from neoxlink_sdk.catalog import CATALOG
from neoxlink_sdk.open_source import load_default_taxonomy_nodes


def test_default_taxonomy_matches_catalog_length() -> None:
    nodes = load_default_taxonomy_nodes()
    assert len(nodes) == len(CATALOG)
    assert {n.code for n in nodes} == {e.code for e in CATALOG}
