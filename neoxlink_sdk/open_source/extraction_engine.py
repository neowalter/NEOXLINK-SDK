from __future__ import annotations

from .intent_parsing import IntentParser
from .schemas import RequestSchema, StructuredIntent
from .taxonomy_mapping import TaxonomyMapper


class ExtractionEngine:
    """Converts raw text into validated structured request schema."""

    def __init__(self, intent_parser: IntentParser, taxonomy_mapper: TaxonomyMapper) -> None:
        self.intent_parser = intent_parser
        self.taxonomy_mapper = taxonomy_mapper

    def extract(self, request_id: str, text: str, entry_kind: str = "demand") -> RequestSchema:
        structured_intent: StructuredIntent = self.intent_parser.parse(text)
        taxonomy_candidates = self.taxonomy_mapper.map(structured_intent)
        return RequestSchema(
            request_id=request_id,
            entry_kind=entry_kind,
            intent=structured_intent,
            taxonomy_candidates=taxonomy_candidates,
        )
