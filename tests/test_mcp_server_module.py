from __future__ import annotations

from neoxlink_sdk.mcp_server import build_adapter


def test_build_adapter_smoke() -> None:
    """`build_adapter` does not require the optional `mcp` package (only stdio run does)."""
    ad = build_adapter()
    names = {t["name"] for t in ad.list_tools()}
    assert "neoxlink.parse_preview" in names
