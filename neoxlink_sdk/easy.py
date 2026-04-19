from __future__ import annotations

from .engine import InMemoryDataSource, ProcurementIntentEngine
from .model_adapters import OpenAIChatCompletionsModel
from .models import MatchCandidate


def create_engine(
    *,
    records: list[MatchCandidate],
    model: str,
    base_url: str | None = None,
    api_key: str | None = None,
    provider_name: str = "openai-compatible",
) -> ProcurementIntentEngine:
    """Create a production-friendly engine in one call.

    This helper keeps onboarding simple: pass your model name, provider URL,
    and dataset records, then run `engine.run(...)`.
    """

    adapter = OpenAIChatCompletionsModel(
        model=model,
        base_url=base_url,
        api_key=api_key,
        provider_name=provider_name,
    )
    return ProcurementIntentEngine(
        data_source=InMemoryDataSource(records),
        model_adapter=adapter,
    )
