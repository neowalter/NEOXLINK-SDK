from __future__ import annotations

from unittest.mock import MagicMock

from neoxlink_sdk.mcp import NeoxlinkMCPAdapter
from neoxlink_sdk.models import ParsedPreview, ParseDraft, UNSPSCClassification
from neoxlink_sdk.skill import NeoxlinkSkill


def _make_preview() -> ParseDraft:
    p = ParsedPreview(
        intent="test",
        entry_kind="demand",
        category="c",
        summary="s",
        confidence=0.9,
        unspsc=UNSPSCClassification(
            code="80101500", name="Business and corporate management consultation services", confidence=0.8
        ),
    )
    return ParseDraft(confirmation_token="tok-1", preview=p)


def test_list_tools_includes_core_names() -> None:
    pl = MagicMock()
    skill = NeoxlinkSkill(pl)
    adapter = NeoxlinkMCPAdapter(skill, engine=None)
    names = {t["name"] for t in adapter.list_tools()}
    assert "neoxlink.parse_preview" in names
    assert "neoxlink.confirmed_submit" in names
    assert "neoxlink.match_intent" not in names


def test_call_parse_preview() -> None:
    pl = MagicMock()
    pl.parse = MagicMock(return_value=_make_preview())
    skill = NeoxlinkSkill(pl)
    adapter = NeoxlinkMCPAdapter(skill, engine=None)
    out = adapter.call_tool("neoxlink.parse_preview", {"text": "hello", "entry_kind": "demand"})
    pl.parse.assert_called_once()
    assert out.get("status") in ("preview_ready", "confirmed")


def test_match_intent_without_engine_errors() -> None:
    pl = MagicMock()
    pl.parse = MagicMock(return_value=_make_preview())
    skill = NeoxlinkSkill(pl)
    adapter = NeoxlinkMCPAdapter(skill, engine=None)
    try:
        adapter.call_tool("neoxlink.match_intent", {"text": "x"})
    except ValueError as e:
        assert "match_intent" in str(e).lower() or "engine" in str(e).lower()
    else:
        raise AssertionError("expected ValueError")
