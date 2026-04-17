from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

EntryKindLiteral = Literal["demand", "supply"]


class UNSPSCClassification(BaseModel):
    code: str = Field(pattern=r"^\d{8}$")
    name: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: Literal["sdk_heuristic", "backend", "manual_override"] = "sdk_heuristic"


class ParsedPreview(BaseModel):
    intent: str
    entry_kind: EntryKindLiteral
    category: str
    entities: list[dict[str, Any]] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    keywords: list[str] = Field(default_factory=list)
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    quality_flags: dict[str, Any] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    unspsc: UNSPSCClassification | None = None
    schema_version: str = "v2"


class ParseDraft(BaseModel):
    confirmation_token: str
    preview: ParsedPreview
    parser_version: str | None = None


class ConfirmedEntry(BaseModel):
    raw_entry_id: str
    entry_kind: EntryKindLiteral
    status: str | None = None
    structured_data: ParsedPreview | dict[str, Any] | None = None


class ResolveResult(BaseModel):
    path: str
    reason: str | None = None
    answer: str | None = None
    suggested_query: str | None = None
    related_results: list[dict[str, Any]] = Field(default_factory=list)


class PipelineOutcome(BaseModel):
    parse: ParseDraft
    confirmed: ConfirmedEntry | None = None
    resolve: ResolveResult | None = None
    skipped_by_user: bool = False


class SkillRequest(BaseModel):
    text: str
    entry_kind: EntryKindLiteral = "demand"
    metadata: dict[str, Any] = Field(default_factory=dict)
    auto_confirm: bool = False
    overrides: dict[str, Any] = Field(default_factory=dict)
    resolve_after_confirm: bool = True


class SkillResponse(BaseModel):
    status: Literal["preview_ready", "confirmed", "skipped"]
    draft: ParseDraft
    confirmed: ConfirmedEntry | None = None
    resolve: ResolveResult | None = None
