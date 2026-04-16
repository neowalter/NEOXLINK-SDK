from __future__ import annotations

import hashlib
import re


def normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def exact_sha256(value: str) -> str:
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def simple_simhash64(value: str) -> int:
    tokens = normalize_text(value).split(" ")
    vector = [0] * 64
    for token in tokens:
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        for idx in range(64):
            bit = 1 if (h >> idx) & 1 else -1
            vector[idx] += bit
    fingerprint = 0
    for idx, score in enumerate(vector):
        if score >= 0:
            fingerprint |= 1 << idx
    return fingerprint


def hamming_distance64(lhs: int, rhs: int) -> int:
    return (lhs ^ rhs).bit_count()
