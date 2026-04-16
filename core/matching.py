from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MatchFeatures:
    keyword_overlap: float
    entity_fit: float
    region_fit: float
    constraint_fit: float
    embedding_sim: float


def weighted_score(features: MatchFeatures) -> float:
    score = (
        features.keyword_overlap * 0.25
        + features.entity_fit * 0.20
        + features.region_fit * 0.20
        + features.constraint_fit * 0.15
        + features.embedding_sim * 0.20
    )
    return max(0.0, min(1.0, score))
