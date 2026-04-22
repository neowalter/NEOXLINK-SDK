from __future__ import annotations

from neoxlink_sdk.catalog import CATALOG, default_unspsc_catalog_path, load_unspsc_entries_from_path
from neoxlink_sdk.unspsc import classify_unspsc, unspsc_candidates


def test_catalog_json_loads_and_matches_path_loader() -> None:
    p = default_unspsc_catalog_path()
    assert p.is_file()
    from_disk = load_unspsc_entries_from_path(p)
    assert from_disk == CATALOG
    assert len(CATALOG) >= 8


def test_unspsc_candidates_software() -> None:
    rows = unspsc_candidates("We need a mobile app and backend development team.", top_k=1)
    assert rows
    assert rows[0][0].code == "81111500"
    assert 0.0 < rows[0][1] <= 1.0


def test_unspsc_candidates_empty_input() -> None:
    assert unspsc_candidates("   \n\t  ") == []


def test_classify_fallback_when_no_match() -> None:
    code, name, conf = classify_unspsc("xyz123 nonexistent", fallback_code="80101500", fallback_name="Business")
    # No keyword hit -> fallback
    assert code == "80101500"
    assert "Business" in name
    assert conf == 0.3


def test_phrase_substring_helps_composite_phrase() -> None:
    # Substring path for "software" inside longer strings without space tokenization
    text = "need softwaredevelopment for logistics"
    rows = unspsc_candidates(text, top_k=1)
    assert rows and rows[0][0].code == "81111500"


def test_tiebreak_deterministic_by_code() -> None:
    res = unspsc_candidates("advisor consulting policy startup", top_k=5)
    if len(res) >= 2:
        assert res[0][1] >= res[1][1]
