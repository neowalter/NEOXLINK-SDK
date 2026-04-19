"""Template: custom ranking strategy plugin."""

from neoxlink_sdk import MatchCandidate, NormalizedIntent


def custom_ranking_strategy(
    signals: dict[str, float],
    intent: NormalizedIntent,
    candidate: MatchCandidate,
) -> float:
    # TODO: tailor weights by domain, category, or business objective.
    _ = (intent, candidate)
    score = (
        (signals.get("semantic_relevance", 0.0) * 0.3)
        + (signals.get("historical_performance", 0.0) * 0.25)
        + (signals.get("intent_fit", 0.0) * 0.3)
        + (signals.get("recency", 0.0) * 0.15)
    )
    return min(1.0, max(0.0, score))
