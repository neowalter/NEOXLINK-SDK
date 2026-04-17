from __future__ import annotations

from typing import Any

from .models import SkillRequest, SkillResponse
from .pipeline import StructuredSubmissionPipeline


class NeoxlinkSkill:
    """Skill-friendly wrapper around the structured submission pipeline."""

    def __init__(self, pipeline: StructuredSubmissionPipeline) -> None:
        self.pipeline = pipeline

    def run(self, request: SkillRequest | dict[str, Any]) -> SkillResponse:
        req = request if isinstance(request, SkillRequest) else SkillRequest.model_validate(request)
        draft = self.pipeline.parse(text=req.text, entry_kind=req.entry_kind, metadata=req.metadata)

        if not req.auto_confirm:
            return SkillResponse(status="preview_ready", draft=draft)

        confirmed = self.pipeline.confirm(draft=draft, overrides=req.overrides)
        resolved = self.pipeline.resolve(confirmed.raw_entry_id) if req.resolve_after_confirm else None
        return SkillResponse(status="confirmed", draft=draft, confirmed=confirmed, resolve=resolved)
