from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EntryKind(StrEnum):
    DEMAND = "demand"
    SUPPLY = "supply"
    UNKNOWN = "unknown"


class BudgetConstraint(BaseModel):
    amount: float | None = None
    currency: str | None = None


class Constraints(BaseModel):
    budget: BudgetConstraint = Field(default_factory=BudgetConstraint)
    timeline: str | None = None
    region: list[str] = Field(default_factory=list)


class Entity(BaseModel):
    name: str
    type: str
    value: str


class QualityFlags(BaseModel):
    needs_review: bool = False
    reason: str = ""


class StructuredRecordV1(BaseModel):
    intent: str
    entry_kind: EntryKind
    category: str
    entities: list[Entity] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)
    keywords: list[str] = Field(default_factory=list)
    summary: str
    normalized_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    quality_flags: QualityFlags = Field(default_factory=QualityFlags)
    schema_version: str = "v1"

    def dict_for_db(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json")
        payload.pop("schema_version", None)
        return payload
