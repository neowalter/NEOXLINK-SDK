"""Async HTTP client for neoxailink.com APIs (``httpx.AsyncClient``)."""

from __future__ import annotations

from typing import Any

import httpx


class AsyncNeoXlinkClient:
    """Async counterpart to :class:`~neoxlink_sdk.client.NeoXlinkClient`.

    Use this in asyncio services, MCP servers, and high-concurrency agents. The
    request paths and payloads match the synchronous client.
    """

    def __init__(
        self,
        base_url: str = "https://neoxailink.com",
        api_key: str | None = None,
        timeout: float = 20.0,
        transport: Any = None,
    ) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        kwargs: dict[str, Any] = {
            "base_url": base_url.rstrip("/"),
            "timeout": timeout,
            "headers": headers,
        }
        if transport is not None:
            kwargs["transport"] = transport
        self._client = httpx.AsyncClient(**kwargs)

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        response = await self._client.request(method, path, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    async def submit_entry(
        self,
        raw_text: str,
        entry_kind: str | None = None,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"raw_text": raw_text, "metadata": metadata or {}}
        if entry_kind:
            payload["entry_kind"] = entry_kind
        req_headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        return await self._request("POST", "/v1/entries", json=payload, headers=req_headers)

    async def get_entry(self, raw_entry_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/entries/{raw_entry_id}")

    async def search(
        self,
        query: str,
        filters: dict[str, list[str]] | None = None,
        entry_kind: str | None = None,
        top_k: int = 20,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query, "filters": filters or {}, "top_k": top_k}
        if entry_kind:
            payload["entry_kind"] = entry_kind
        return await self._request("POST", "/v1/search", json=payload)

    async def parse_entry(
        self,
        raw_text: str,
        entry_kind: str = "demand",
        metadata: dict[str, Any] | None = None,
        use_own_model: bool = False,
    ) -> dict[str, Any]:
        payload_metadata = dict(metadata or {})
        payload_metadata.setdefault("billing", {})
        if isinstance(payload_metadata["billing"], dict):
            payload_metadata["billing"].setdefault("use_own_model", use_own_model)
        payload: dict[str, Any] = {
            "entry_kind": entry_kind,
            "raw_text": raw_text,
            "metadata": payload_metadata,
        }
        return await self._request("POST", "/v1/entries/parse", json=payload)

    async def confirm_entry(
        self,
        confirmation_token: str,
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {"confirmation_token": confirmation_token, "overrides": overrides or {}}
        return await self._request("POST", "/v1/entries/confirm", json=payload)

    async def resolve_entry(self, raw_entry_id: str) -> dict[str, Any]:
        payload = {"raw_entry_id": raw_entry_id}
        return await self._request("POST", "/v1/entries/resolve", json=payload)

    async def structured_submit(
        self,
        raw_text: str,
        entry_kind: str = "demand",
        metadata: dict[str, Any] | None = None,
        overrides: dict[str, Any] | None = None,
        use_own_model: bool = False,
    ) -> dict[str, Any]:
        parse_payload = await self.parse_entry(
            raw_text=raw_text,
            entry_kind=entry_kind,
            metadata=metadata,
            use_own_model=use_own_model,
        )
        confirmation_token = str(parse_payload["confirmation_token"])
        confirm_payload = await self.confirm_entry(confirmation_token=confirmation_token, overrides=overrides)
        return {"parse": parse_payload, "confirm": confirm_payload}

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncNeoXlinkClient":
        return self

    async def __aexit__(self, _exc_type: Any, _exc: Any, _tb: Any) -> None:
        await self.aclose()
