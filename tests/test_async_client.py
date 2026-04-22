from __future__ import annotations

import asyncio
from typing import Any

import httpx

from neoxlink_sdk.async_client import AsyncNeoXlinkClient
from neoxlink_sdk.async_pipeline import AsyncStructuredSubmissionPipeline
from neoxlink_sdk.models import ParsedPreview, UNSPSCClassification


def _sample_preview() -> dict[str, Any]:
    p = ParsedPreview(
        intent="test",
        entry_kind="demand",
        category="cat",
        summary="summary",
        confidence=0.9,
        unspsc=UNSPSCClassification(code="81111500", name="Custom software", confidence=0.5),
    )
    return p.model_dump()


def _make_mock_transport() -> httpx.MockTransport:
    prev = _sample_preview()

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "POST" and path == "/v1/entries/parse":
            return httpx.Response(
                200,
                json={"confirmation_token": "tok-1", "preview": prev, "parser_version": "1"},
            )
        if request.method == "POST" and path == "/v1/entries/confirm":
            return httpx.Response(
                200,
                json={"raw_entry_id": "e1", "entry_kind": "demand", "status": "ok"},
            )
        if request.method == "POST" and path == "/v1/entries/resolve":
            return httpx.Response(
                200,
                json={"path": "/r", "reason": "done", "answer": "ok", "suggested_query": None, "related_results": []},
            )
        return httpx.Response(404, json={"error": "not found"})

    return httpx.MockTransport(handler)


def test_async_client_parse_roundtrip() -> None:
    async def main() -> None:
        client = AsyncNeoXlinkClient(
            base_url="https://test.example",
            api_key="k",
            transport=_make_mock_transport(),
        )
        try:
            out = await client.parse_entry("need software", entry_kind="demand")
            assert out["confirmation_token"] == "tok-1"
            assert out["preview"]["unspsc"]["code"] == "81111500"
        finally:
            await client.aclose()

    asyncio.run(main())


def test_async_pipeline_run() -> None:
    async def main() -> None:
        aclient = AsyncNeoXlinkClient(
            base_url="https://test.example",
            api_key="k",
            transport=_make_mock_transport(),
        )
        try:
            pipeline = AsyncStructuredSubmissionPipeline(aclient)
            outcome = await pipeline.run("need software", resolve_after_confirm=True)
            assert outcome.parse.confirmation_token == "tok-1"
            assert outcome.confirmed is not None
            assert outcome.confirmed.raw_entry_id == "e1"
            assert outcome.resolve is not None
            assert outcome.resolve.path == "/r"
        finally:
            await aclient.aclose()

    asyncio.run(main())
