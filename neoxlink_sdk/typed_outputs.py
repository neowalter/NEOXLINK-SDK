from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError, model_validator


class TypedLLMOutput(BaseModel):
    """Strict normalized shape for LLM structured output."""

    intent: str = Field(min_length=3)
    confidence: float = Field(ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_tags(self) -> "TypedLLMOutput":
        cleaned = []
        for tag in self.tags:
            token = str(tag).strip()
            if not token:
                continue
            cleaned.append(token.lower())
        if not cleaned:
            raise ValueError("tags must contain at least one non-empty label")
        self.tags = list(dict.fromkeys(cleaned))
        return self


def parse_typed_output(payload: dict[str, Any]) -> TypedLLMOutput:
    return TypedLLMOutput.model_validate(payload)


def try_parse_typed_output(payload: dict[str, Any]) -> tuple[TypedLLMOutput | None, str | None]:
    try:
        return parse_typed_output(payload), None
    except ValidationError as exc:
        return None, str(exc)
