import pytest

from neoxlink_sdk.typed_outputs import parse_typed_output


def test_parse_typed_output_normalizes_tags() -> None:
    parsed = parse_typed_output(
        {"intent": "match supplier", "confidence": 0.9, "tags": ["MCP", "mcp", " Agent "], "attributes": {}}
    )
    assert parsed.tags == ["mcp", "agent"]


def test_parse_typed_output_requires_nonempty_tags() -> None:
    with pytest.raises(Exception):
        parse_typed_output({"intent": "match supplier", "confidence": 0.9, "tags": [" "], "attributes": {}})
