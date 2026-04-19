"""Template: custom model adapter plugin."""

from neoxlink_sdk import HeuristicModelAdapter, MatchCandidate, NormalizedIntent, ParsedIntent, UNSPSCCandidate


class CustomModelAdapter:
    provider_name = "your-provider"
    model_name = "your-model"

    def __init__(self) -> None:
        self._fallback = HeuristicModelAdapter()

    def parse_intent(self, text: str) -> ParsedIntent:
        # TODO: call your provider API and convert output into ParsedIntent.
        return self._fallback.parse_intent(text)

    def disambiguate_unspsc(self, text: str, candidates: list[UNSPSCCandidate]) -> list[UNSPSCCandidate]:
        # TODO: optional provider-side reranking of UNSPSC candidates.
        return self._fallback.disambiguate_unspsc(text, candidates)

    def score_match(self, normalized_intent: NormalizedIntent, candidate: MatchCandidate) -> dict[str, float]:
        # TODO: return deterministic relevance signals.
        return self._fallback.score_match(normalized_intent, candidate)
