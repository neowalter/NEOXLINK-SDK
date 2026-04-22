from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

SCHEMA_VERSION = "v1.0.0"


class StructuredIntent(BaseModel):
    product_or_service: str
    requirements: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    language: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    raw_input: str
    schema_version: str = SCHEMA_VERSION


class RequestSchema(BaseModel):
    request_id: str
    entry_kind: str = Field(pattern=r"^(demand|supply)$")
    intent: StructuredIntent
    taxonomy_candidates: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION


class ProviderSchema(BaseModel):
    provider_id: str
    name: str
    description: str
    categories: list[str] = Field(default_factory=list)
    location: str | None = None
    public_source_ref: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION


class MatchResultSchema(BaseModel):
    request_id: str
    provider_id: str
    score: float = Field(ge=0.0, le=1.0)
    reason_signals: dict[str, float] = Field(default_factory=dict)
    matched_constraints: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION


class FeedbackSchema(BaseModel):
    request_id: str
    provider_id: str
    accepted: bool
    comments: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION
