"""Stable import path for quick starts: ``from neoxlink import SDK``."""

from __future__ import annotations

from typing import Any

from neoxlink_sdk.client import NeoXlinkClient
from neoxlink_sdk.pipeline import StructuredSubmissionPipeline

__all__ = ["SDK"]


class SDK:
    """Facade over :class:`~neoxlink_sdk.pipeline.StructuredSubmissionPipeline` for structured parsing."""

    def __init__(
        self,
        *,
        base_url: str = "https://neoxailink.com",
        api_key: str,
    ) -> None:
        self._pipeline = StructuredSubmissionPipeline(
            NeoXlinkClient(base_url=base_url, api_key=api_key),
        )

    @property
    def pipeline(self) -> StructuredSubmissionPipeline:
        return self._pipeline

    def parse_preview(
        self,
        text: str,
        entry_kind: str = "demand",
        metadata: dict[str, Any] | None = None,
        use_own_model: bool = False,
    ):
        """Run LLM-backed **Structured Preview** (UNSPSC **Code + Name** when available)."""
        return self._pipeline.parse(
            text=text,
            entry_kind=entry_kind,
            metadata=metadata,
            use_own_model=use_own_model,
        )
