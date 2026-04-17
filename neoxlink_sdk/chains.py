from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .models import PipelineOutcome
from .pipeline import StructuredSubmissionPipeline


class SubmissionChainInput(BaseModel):
    """LangChain-style invocation payload."""

    text: str
    entry_kind: str = Field(default="demand", pattern=r"^(demand|supply)$")
    metadata: dict[str, Any] = Field(default_factory=dict)
    resolve_after_confirm: bool = True
    auto_confirm: bool = True
    overrides: dict[str, Any] = Field(default_factory=dict)


class NeoxlinkSubmissionChain:
    """Composable chain wrapper over the neoxlink structured pipeline.

    This class intentionally mirrors a minimal `invoke()` ergonomics similar to
    chain-centric SDKs.
    """

    def __init__(self, pipeline: StructuredSubmissionPipeline) -> None:
        self._pipeline = pipeline

    def invoke(self, input: SubmissionChainInput | dict[str, Any]) -> PipelineOutcome:
        payload = input if isinstance(input, SubmissionChainInput) else SubmissionChainInput.model_validate(input)
        if payload.auto_confirm:
            return self._pipeline.run(
                text=payload.text,
                entry_kind=payload.entry_kind,
                metadata=payload.metadata,
                resolve_after_confirm=payload.resolve_after_confirm,
                confirm_handler=lambda _draft: payload.overrides,
            )

        draft = self._pipeline.parse(text=payload.text, entry_kind=payload.entry_kind, metadata=payload.metadata)
        return PipelineOutcome(parse=draft, confirmed=None, resolve=None, skipped_by_user=True)
