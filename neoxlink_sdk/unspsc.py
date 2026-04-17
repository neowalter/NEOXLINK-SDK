from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class UNSPSCEntry:
    code: str
    name: str
    keywords: tuple[str, ...]


# Curated, high-signal subset for neoxlink demand/supply workflows.
UNSPSC_CATALOG: tuple[UNSPSCEntry, ...] = (
    UNSPSCEntry(
        code="80101500",
        name="Business and corporate management consultation services",
        keywords=("advisor", "advisory", "consulting", "consultant", "strategy", "policy", "startup"),
    ),
    UNSPSCEntry(
        code="81111500",
        name="Software or applications development services",
        keywords=("software", "application", "app", "development", "developer", "engineering"),
    ),
    UNSPSCEntry(
        code="81112100",
        name="Internet services",
        keywords=("internet", "web", "website", "online", "cloud", "platform"),
    ),
    UNSPSCEntry(
        code="80141600",
        name="Sales and business promotion activities",
        keywords=("marketing", "promotion", "growth", "campaign", "lead", "acquisition"),
    ),
    UNSPSCEntry(
        code="44121500",
        name="Packaging materials",
        keywords=("packaging", "box", "boxes", "carton", "kraft", "label", "shipment"),
    ),
    UNSPSCEntry(
        code="86101700",
        name="Training services",
        keywords=("training", "coach", "coaching", "workshop", "education", "course"),
    ),
    UNSPSCEntry(
        code="81161700",
        name="Telecommunications support services",
        keywords=("telecom", "network", "infrastructure", "operations", "support"),
    ),
    UNSPSCEntry(
        code="85121800",
        name="Medical laboratories and providers",
        keywords=("medical", "health", "clinic", "diagnostic", "laboratory"),
    ),
)


def _normalize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [token for token in tokens if token]


def unspsc_candidates(text: str, top_k: int = 3) -> list[tuple[UNSPSCEntry, float]]:
    """Return top UNSPSC candidates with deterministic confidence values."""
    tokens = set(_normalize(text))
    if not tokens:
        return []

    scored: list[tuple[UNSPSCEntry, float]] = []
    for entry in UNSPSC_CATALOG:
        keyword_set = set(entry.keywords)
        overlap = len(tokens.intersection(keyword_set))
        if overlap == 0:
            continue
        precision = overlap / max(1, len(tokens))
        recall = overlap / max(1, len(keyword_set))
        score = min(1.0, max(0.2, (precision * 0.45) + (recall * 0.55)))
        scored.append((entry, score))

    scored.sort(key=lambda item: item[1], reverse=True)
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
