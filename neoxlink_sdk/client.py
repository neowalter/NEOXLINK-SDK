from __future__ import annotations

from typing import Any

import httpx


class NeoXlinkClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 20.0) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

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
        response = self._client.post("/v1/entries", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
