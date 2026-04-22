from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from neoxlink_sdk.engine import HeuristicModelAdapter
from neoxlink_sdk.models import ParsedIntent


def test_heuristic_parse_intent_produces_valid_parsed_intent() -> None:
    h = HeuristicModelAdapter()
    text = (
        "We are looking to procure 500 kraft paper cartons for retail launch in the EU, "
        "urgent delivery needed."
    )
    p = h.parse_intent(text)
    assert isinstance(p, ParsedIntent)
    assert p.raw_text == text
    assert p.confidence >= 0.0 and p.confidence <= 1.0
    assert "urgency" in p.constraints
    assert p.constraints.get("urgency") == "high"
    assert isinstance(p.ambiguity_signals, list)


def test_parsed_intent_model_dump_is_json_serializable_structured_output() -> None:
    h = HeuristicModelAdapter()
    p = h.parse_intent("We need to buy office supplies in bulk, no rush.")
    data = p.model_dump(mode="json")
    raw = json.dumps(data)
    roundtrip = json.loads(raw)
    restored = ParsedIntent.model_validate(roundtrip)
    assert restored.model_dump() == p.model_dump()
    # Structured "NL → JSON" contract: required keys for downstream systems
    for key in (
        "product_or_service",
        "constraints",
        "quantity_signal",
        "location",
        "budget_hint",
        "temporal_context",
        "ambiguity_signals",
        "confidence",
        "raw_text",
    ):
        assert key in data


def test_parsed_intent_requires_fields() -> None:
    with pytest.raises(ValidationError):
        ParsedIntent()  # type: ignore[call-arg]
