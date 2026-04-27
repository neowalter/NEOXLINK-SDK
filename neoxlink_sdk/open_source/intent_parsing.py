from __future__ import annotations

from dataclasses import dataclass

from ..model_adapters import OpenAIChatCompletionsModel
from .schemas import StructuredIntent


@dataclass(frozen=True)
class PromptTemplate:
    version: str
    system_prompt: str
    output_contract: str
    examples: tuple[str, ...] = ()


DEFAULT_INTENT_PROMPT = PromptTemplate(
    version="intent-v1",
    system_prompt=(
        "You are a business intent parser. Convert natural language to structured intent "
        "for downstream extraction, classification, and matching. Keep the output deterministic and concise."
    ),
    output_contract=(
        "Return JSON with keys: product_or_service,requirements,constraints,language,confidence,raw_input."
    ),
)


class IntentParser:
    """LLM-first intent parser with strict schema validation."""

    def __init__(
        self,
        model: OpenAIChatCompletionsModel,
        template: PromptTemplate = DEFAULT_INTENT_PROMPT,
    ) -> None:
        self.model = model
        self.template = template

    def parse(self, text: str) -> StructuredIntent:
        parsed = self.model.parse_intent(text)
        return StructuredIntent(
            product_or_service=parsed.product_or_service,
            requirements={"quantity_signal": parsed.quantity_signal},
            constraints=parsed.constraints,
            language=None,
            confidence=parsed.confidence,
            raw_input=text,
        )
