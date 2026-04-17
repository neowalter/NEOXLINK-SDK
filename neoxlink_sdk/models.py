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
    use_own_model: bool = False


class SkillResponse(BaseModel):
    status: Literal["preview_ready", "confirmed", "skipped"]
    draft: ParseDraft
    confirmed: ConfirmedEntry | None = None
    resolve: ResolveResult | None = None


class ParsedIntent(BaseModel):
    product_or_service: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    quantity_signal: str | None = None
    location: str | None = None
    budget_hint: str | None = None
    temporal_context: str | None = None
    ambiguity_signals: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    raw_text: str


class UNSPSCCandidate(BaseModel):
    code: str = Field(pattern=r"^\d{8}$")
    name: str
    confidence: float = Field(ge=0.0, le=1.0)


class ClarificationQuestion(BaseModel):
    key: str
    question: str
    reason: str
    required: bool = True


class ClarificationState(BaseModel):
    required: bool
    confidence_threshold: float = Field(ge=0.0, le=1.0)
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    answers: dict[str, str] = Field(default_factory=dict)
    resolved: bool = False


class NormalizedIntent(BaseModel):
    entry_kind: EntryKindLiteral
    unspsc_code: str = Field(pattern=r"^\d{8}$")
    unspsc_name: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    inferred_metadata: dict[str, Any] = Field(default_factory=dict)


class MatchCandidate(BaseModel):
    partner_id: str
    partner_type: Literal["supplier", "buyer"] = "supplier"
    title: str
    description: str
    unspsc_codes: list[str] = Field(default_factory=list)
    location: str | None = None
    recency_days: int = 30
    performance_score: float = Field(ge=0.0, le=1.0, default=0.5)
    attributes: dict[str, Any] = Field(default_factory=dict)


class RankedMatch(BaseModel):
    partner_id: str
    partner_type: Literal["supplier", "buyer"]
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reason_signals: dict[str, float] = Field(default_factory=dict)
    matched_attributes: dict[str, Any] = Field(default_factory=dict)
    source: str


class ModelCallTrace(BaseModel):
    stage: str
    provider: str
    model: str
    latency_ms: float = Field(ge=0.0)
    estimated_cost_usd: float = Field(ge=0.0)


class PipelineStageTrace(BaseModel):
    stage: str
    elapsed_ms: float = Field(ge=0.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    notes: dict[str, Any] = Field(default_factory=dict)


class ProcurementEngineResult(BaseModel):
    parsed_intent: ParsedIntent
    unspsc_candidates: list[UNSPSCCandidate] = Field(default_factory=list)
    clarification: ClarificationState
    normalized_intent: NormalizedIntent
    matches: list[RankedMatch] = Field(default_factory=list)
    traces: list[PipelineStageTrace] = Field(default_factory=list)
    model_calls: list[ModelCallTrace] = Field(default_factory=list)
