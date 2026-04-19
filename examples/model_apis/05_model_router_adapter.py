from neoxlink_sdk import (
    HeuristicModelAdapter,
    MatchCandidate,
    NormalizedIntent,
    OpenAIChatCompletionsModel,
    ParsedIntent,
    UNSPSCCandidate,
)


class ModelRouterAdapter:
    """Routes tasks to provider adapters by request complexity and deployment policy."""

    provider_name = "router"
    model_name = "dynamic"

    def __init__(
        self,
        *,
        fast_adapter=None,
        reasoning_adapter=None,
        low_cost_adapter=None,
        local_adapter=None,
        default_openai_client=None,
        fast_model: str | None = None,
        reasoning_model: str | None = None,
        low_cost_model: str | None = None,
        local_model: str | None = None,
        local_base_url: str | None = None,
    ) -> None:
        self.fallback = HeuristicModelAdapter()
        self.fast = fast_adapter or self._build_adapter(
            model=fast_model,
            provider_name="router-fast",
            openai_client=default_openai_client,
        )
        self.reasoning = reasoning_adapter or self._build_adapter(
            model=reasoning_model,
            provider_name="router-reasoning",
            openai_client=default_openai_client,
        )
        self.low_cost = low_cost_adapter or self._build_adapter(
            model=low_cost_model,
            provider_name="router-low-cost",
            openai_client=default_openai_client,
        )
        self.local = local_adapter or self._build_adapter(
            model=local_model,
            provider_name="router-local",
            base_url=local_base_url,
            openai_client=default_openai_client,
        )

    def _build_adapter(
        self,
        *,
        model: str | None,
        provider_name: str,
        base_url: str | None = None,
        openai_client=None,
    ):
        if not model:
            return self.fallback
        return OpenAIChatCompletionsModel(
            model=model,
            base_url=base_url,
            openai_client=openai_client,
            provider_name=provider_name,
        )

    def _select_provider(self, text: str):
        lowered = text.lower()
        if "offline" in lowered or "local only" in lowered:
            self.provider_name, self.model_name = self.local.provider_name, self.local.model_name
            return self.local
        if len(text) > 220:
            self.provider_name, self.model_name = self.reasoning.provider_name, self.reasoning.model_name
            return self.reasoning
        if "cheap" in lowered or "budget" in lowered:
            self.provider_name, self.model_name = self.low_cost.provider_name, self.low_cost.model_name
            return self.low_cost
        self.provider_name, self.model_name = self.fast.provider_name, self.fast.model_name
        return self.fast

    def parse_intent(self, text: str) -> ParsedIntent:
        adapter = self._select_provider(text)
        try:
            return adapter.parse_intent(text)
        except Exception:
            self.provider_name, self.model_name = self.fallback.provider_name, self.fallback.model_name
            return self.fallback.parse_intent(text)

    def infer_unspsc_candidates(self, text: str, top_k: int = 5) -> list[UNSPSCCandidate]:
        return self.fallback.infer_unspsc_candidates(text, top_k=top_k)

    def score_match(self, normalized_intent: NormalizedIntent, candidate: MatchCandidate) -> dict[str, float]:
        return self.fallback.score_match(normalized_intent, candidate)


if __name__ == "__main__":
    adapter = ModelRouterAdapter(
        fast_model="gpt-4o-mini",
        reasoning_model="gpt-4o",
        low_cost_model="gpt-4o-mini",
        local_model="qwen2.5:7b",
        local_base_url="http://localhost:11434/v1",
    )
    parsed = adapter.parse_intent("Need urgent startup policy advisor in Shanghai with local only fallback")
    print(adapter.provider_name, adapter.model_name)
    print(parsed.model_dump())
