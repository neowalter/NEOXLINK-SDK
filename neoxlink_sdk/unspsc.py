"""UNSPSC keyword retrieval over the packaged subset (single source: `catalog.CATALOG`)."""

from __future__ import annotations

from .catalog import CATALOG as UNSPSC_CATALOG
from .catalog import KEYWORD_IDF, UNSPSCEntry

# Re-export for backward compatibility
__all__ = ["UNSPSCEntry", "UNSPSC_CATALOG", "classify_unspsc", "unspsc_candidates"]


def _normalize(text: str) -> list[str]:
    lowered = text.lower()
    for punct in (".", ",", ";", ":", "!", "?", "(", ")", "[", "]", "{", "}", "\"", "'"):
        lowered = lowered.replace(punct, " ")
    return [token for token in lowered.split() if token]


def _phrase_idf_score(text_lower: str, entry: UNSPSCEntry, idf: dict[str, float]) -> float:
    """Reward longer keyword substrings that appear in raw text but may be missed by whitespace tokenization."""
    total = 0.0
    for kw in entry.keywords:
        if len(kw) < 3:
            continue
        if kw in text_lower:
            total += idf.get(kw, 0.0)
    return min(1.0, total / 3.0)


def _idf_token_overlap(tokens: set[str], keyword_set: set[str], idf: dict[str, float]) -> float:
    inter = tokens.intersection(keyword_set)
    if not inter:
        return 0.0
    num = sum(idf.get(t, 0.0) for t in inter)
    den = sum(idf.get(t, 0.0) for t in tokens) or 1.0
    return num / den


def unspsc_candidates(text: str, top_k: int = 3) -> list[tuple[UNSPSCEntry, float]]:
    """Return top UNSPSC candidates with deterministic confidence values.

    Scoring blends token precision/recall on keyword sets with IDF-weighted overlap
    and a substring/phrase term for und tokenized product names.
    """
    idf = KEYWORD_IDF
    text_lower = text.lower()
    tokens = set(_normalize(text))
    if not tokens and not any(len(k) >= 3 and k in text_lower for e in UNSPSC_CATALOG for k in e.keywords):
        return []

    scored: list[tuple[UNSPSCEntry, float]] = []
    for entry in UNSPSC_CATALOG:
        keyword_set = set(entry.keywords)
        overlap = len(tokens.intersection(keyword_set))
        if overlap == 0 and not any(len(k) >= 3 and k in text_lower for k in entry.keywords):
            continue

        if overlap == 0:
            base = 0.22
        else:
            precision = overlap / max(1, len(tokens))
            recall = overlap / max(1, len(keyword_set))
            base = min(1.0, max(0.2, (precision * 0.45) + (recall * 0.55)))

        idf_component = _idf_token_overlap(tokens, keyword_set, idf) if tokens else 0.0
        phrase = _phrase_idf_score(text_lower, entry, idf)
        score = min(1.0, max(0.2, 0.48 * base + 0.32 * idf_component + 0.20 * phrase))
        scored.append((entry, score))

    scored.sort(key=lambda item: (item[1], item[0].code), reverse=True)
    if not scored:
        return []
    return scored[: max(1, top_k)]


def classify_unspsc(
    text: str,
    *,
    fallback_code: str = "80101500",
    fallback_name: str = "Business and corporate management consultation services",
) -> tuple[str, str, float]:
    """Return UNSPSC code/name/confidence for free text.

    Confidence is heuristic and normalized to [0, 1].
    """
    candidates = unspsc_candidates(text=text, top_k=1)
    if not candidates:
        return fallback_code, fallback_name, 0.3
    best, score = candidates[0]
    return best.code, best.name, min(1.0, max(0.35, score + 0.2))
