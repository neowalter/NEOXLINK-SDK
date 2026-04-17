from __future__ import annotations

from typing import Any

import httpx


class NeoXlinkClient:
    """HTTP SDK client for neoxailink.com APIs.

    The client keeps backward-compatible methods (`submit_entry`, `search`, etc.)
    and also exposes the parse -> confirm -> resolve workflow for structured flows.
    """

    def __init__(
        self,
        base_url: str = "https://neoxailink.com",
        api_key: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout, headers=headers)

    def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        response = self._client.request(method, path, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    def submit_entry(
        self,
        raw_text: str,
        entry_kind: str | None = None,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"raw_text": raw_text, "metadata": metadata or {}}
        if entry_kind:
            payload["entry_kind"] = entry_kind
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        return self._request("POST", "/v1/entries", json=payload, headers=headers)

    def get_entry(self, raw_entry_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/entries/{raw_entry_id}")

    def search(
        self,
        query: str,
        filters: dict[str, list[str]] | None = None,
        entry_kind: str | None = None,
        top_k: int = 20,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query, "filters": filters or {}, "top_k": top_k}
        if entry_kind:
            payload["entry_kind"] = entry_kind
        return self._request("POST", "/v1/search", json=payload)

    def parse_entry(
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
        return self._request("POST", "/v1/entries/parse", json=payload)

    def confirm_entry(
        self,
        confirmation_token: str,
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {"confirmation_token": confirmation_token, "overrides": overrides or {}}
        return self._request("POST", "/v1/entries/confirm", json=payload)

    def resolve_entry(self, raw_entry_id: str) -> dict[str, Any]:
        payload = {"raw_entry_id": raw_entry_id}
        return self._request("POST", "/v1/entries/resolve", json=payload)

    def structured_submit(
        self,
        raw_text: str,
        entry_kind: str = "demand",
        metadata: dict[str, Any] | None = None,
        overrides: dict[str, Any] | None = None,
        use_own_model: bool = False,
    ) -> dict[str, Any]:
        """Run parse -> confirm in one call chain.

        Returns both parse preview and final confirmed entry payload.
        """
        parse_payload = self.parse_entry(
            raw_text=raw_text,
            entry_kind=entry_kind,
            metadata=metadata,
            use_own_model=use_own_model,
        )
        confirmation_token = str(parse_payload["confirmation_token"])
        confirm_payload = self.confirm_entry(confirmation_token=confirmation_token, overrides=overrides)
        return {"parse": parse_payload, "confirm": confirm_payload}

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "NeoXlinkClient":
        return self

    def __exit__(self, _exc_type: Any, _exc: Any, _tb: Any) -> None:
        self.close()
