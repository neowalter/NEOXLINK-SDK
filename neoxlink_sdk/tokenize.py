"""Shared whitespace/punctuation normalization for NL → keyword matching (UNSPSC, heuristics)."""

from __future__ import annotations

# Must match legacy behavior: each of these replaced by a single ASCII space before split.
_MATCH_PUNCT_CHARS = '.,;:!?()[]{}"\''

_MATCH_TRANS = str.maketrans({c: " " for c in _MATCH_PUNCT_CHARS})


def matching_token_set(text: str) -> set[str]:
    """Lowercase, map punctuation to spaces, split on whitespace, drop empty tokens."""
    return {t for t in text.lower().translate(_MATCH_TRANS).split() if t}


def matching_token_list(text: str) -> list[str]:
    """Same normalization as `matching_token_set` but preserves token order (including duplicates)."""
    return [t for t in text.lower().translate(_MATCH_TRANS).split() if t]
