from neoxlink_sdk.models import ParsedPreview, ParseDraft, UNSPSCClassification
from neoxlink_sdk.pipeline_core import build_confirm_overrides, build_parse_metadata, parse_structured_data


def test_build_parse_metadata_adds_use_own_model() -> None:
    metadata = build_parse_metadata({"billing": {}}, use_own_model=True)
    assert metadata["billing"]["use_own_model"] is True


def test_build_confirm_overrides_prefers_unspsc_defaults() -> None:
    draft = ParseDraft(
        confirmation_token="tok",
        preview=ParsedPreview(
            intent="need supplier",
            entry_kind="demand",
            category="services",
            summary="summary",
            confidence=0.9,
            unspsc=UNSPSCClassification(code="10101010", name="Example", confidence=0.9),
        ),
    )
    overrides = build_confirm_overrides(draft, {})
    assert overrides["unspsc_code"] == "10101010"
    assert overrides["unspsc_name"] == "Example"


def test_parse_structured_data_returns_raw_on_validation_error() -> None:
    value = {"invalid": "shape"}
    parsed = parse_structured_data(value)
    assert parsed == value
