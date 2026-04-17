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


def classify_unspsc(
    text: str,
    *,
    fallback_code: str = "80101500",
    fallback_name: str = "Business and corporate management consultation services",
) -> tuple[str, str, float]:
    """Return UNSPSC code/name/confidence for free text.

    Confidence is heuristic and normalized to [0, 1].
    """
    tokens = set(_normalize(text))
    if not tokens:
        return fallback_code, fallback_name, 0.2

    best: UNSPSCEntry | None = None
    best_score = 0.0
    for entry in UNSPSC_CATALOG:
        matches = sum(1 for keyword in entry.keywords if keyword in tokens)
        if matches <= 0:
            continue
        score = matches / max(2, len(entry.keywords))
        if score > best_score:
            best_score = score
            best = entry

    if best is None:
        return fallback_code, fallback_name, 0.3
    return best.code, best.name, min(1.0, max(0.35, best_score + 0.25))
