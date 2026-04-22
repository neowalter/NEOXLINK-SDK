from __future__ import annotations

import time
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


def _percentile_ms(samples: list[float], pct: float) -> float:
    s = sorted(samples)
    if not s:
        return 0.0
    idx = min(len(s) - 1, max(0, int((pct / 100.0) * (len(s) - 1))))
    return s[idx] * 1000.0


def test_mcp_call_tool_parse_preview_stays_off_hot_path() -> None:
    """Guards against accidental O(n) work on each MCP tool call (local mock; no network)."""
    pl = MagicMock()
    pl.parse = MagicMock(return_value=_make_preview())
    skill = NeoxlinkSkill(pl)
    adapter = NeoxlinkMCPAdapter(skill, engine=None)
    n = 200
    samples: list[float] = []
    for _ in range(n):
        t0 = time.perf_counter()
        adapter.call_tool(
            "neoxlink.parse_preview",
            {"text": "procurement of packaging cartons", "entry_kind": "demand"},
        )
        samples.append(time.perf_counter() - t0)
    p95 = _percentile_ms(samples, 95.0)
    # In-process call with mocks should stay on a cool path; allow CI noise.
    assert p95 < 25.0, f"p95 latency too high: {p95:.3f}ms"
