from __future__ import annotations

from typing import Any

from .models import ParsedPreview, ParseDraft


def build_parse_metadata(metadata: dict[str, Any] | None, use_own_model: bool) -> dict[str, Any]:
    parse_metadata = dict(metadata or {})
    parse_metadata.setdefault("billing", {})
    if isinstance(parse_metadata["billing"], dict):
        parse_metadata["billing"].setdefault("use_own_model", use_own_model)
    return parse_metadata


def build_confirm_overrides(draft: ParseDraft, overrides: dict[str, Any] | None) -> dict[str, Any]:
    confirm_overrides = dict(overrides or {})
    if draft.preview.unspsc:
        confirm_overrides.setdefault("unspsc_code", draft.preview.unspsc.code)
        confirm_overrides.setdefault("unspsc_name", draft.preview.unspsc.name)
    return confirm_overrides


def parse_structured_data(value: Any) -> ParsedPreview | dict[str, Any] | Any:
    if not isinstance(value, dict):
        return value
    try:
        return ParsedPreview.model_validate(value)
    except Exception:
        return value
