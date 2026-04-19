from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Protocol

import httpx


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    backoff_seconds: float = 1.0


@dataclass(frozen=True)
class ConnectorRecord:
    source_url: str
    raw_text: str
    metadata: dict[str, str]


class PublicDataConnector(Protocol):
    def fetch(self) -> list[ConnectorRecord]:
        """Fetch publicly available records only."""


class PublicHTTPConnector:
    """Generic connector for public HTTP endpoints returning text payloads."""

    def __init__(self, source_url: str, retry: RetryPolicy | None = None) -> None:
        self.source_url = source_url
        self.retry = retry or RetryPolicy()

    def fetch(self) -> list[ConnectorRecord]:
        last_error: Exception | None = None
        for attempt in range(1, self.retry.attempts + 1):
            try:
                with httpx.Client(timeout=20.0) as client:
                    response = client.get(self.source_url)
                    response.raise_for_status()
                    text = response.text
                return [
                    ConnectorRecord(
                        source_url=self.source_url,
                        raw_text=text,
                        metadata={"attempt": str(attempt)},
                    )
                ]
            except Exception as exc:  # pragma: no cover
                last_error = exc
                if attempt < self.retry.attempts:
                    sleep(self.retry.backoff_seconds * attempt)
        if last_error is not None:
            raise last_error
        return []
