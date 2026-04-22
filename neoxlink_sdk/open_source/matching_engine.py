from __future__ import annotations

from dataclasses import dataclass

from ..model_adapters import OpenAIChatCompletionsModel
from .schemas import MatchResultSchema, ProviderSchema, RequestSchema


@dataclass(frozen=True)
class ScoringPolicy:
    weights: dict[str, float] | None = None


class MatchingEngine:
    """Generic matching pipeline without proprietary fixed ranking weights."""

    def __init__(self, model: OpenAIChatCompletionsModel, scoring_policy: ScoringPolicy | None = None) -> None:
        self.model = model
        self.scoring_policy = scoring_policy or ScoringPolicy(weights=None)

    def _weighted_score(self, signals: dict[str, float]) -> float:
        if not signals:
            return 0.0
        weights = self.scoring_policy.weights
        if not weights:
            return sum(signals.values()) / len(signals)
        numerator = 0.0
        denominator = 0.0
        for key, value in signals.items():
            weight = max(0.0, float(weights.get(key, 0.0)))
            numerator += value * weight
            denominator += weight
        if denominator <= 0.0:
            return sum(signals.values()) / len(signals)
        return numerator / denominator

    def match(self, request: RequestSchema, providers: list[ProviderSchema], top_k: int = 5) -> list[MatchResultSchema]:
        results: list[MatchResultSchema] = []
        for provider in providers:
            signals = {
                "semantic_relevance": 0.5,
                "intent_fit": 0.5,
                "taxonomy_fit": 0.5,
            }
            if request.taxonomy_candidates:
                codes = {str(item["code"]) for item in request.taxonomy_candidates if "code" in item}
                provider_codes = set(provider.categories)
                if codes.intersection(provider_codes):
                    signals["taxonomy_fit"] = 0.9
            score = max(0.0, min(1.0, self._weighted_score(signals)))
            results.append(
                MatchResultSchema(
                    request_id=request.request_id,
                    provider_id=provider.provider_id,
                    score=score,
                    reason_signals=signals,
                    matched_constraints={"location": provider.location},
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        return results[: max(1, top_k)]
