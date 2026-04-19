from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..model_adapters import OpenAIChatCompletionsModel
from .schemas import StructuredIntent


@dataclass(frozen=True)
class TaxonomyNode:
    code: str
    name: str
    keywords: tuple[str, ...] = ()


class TaxonomyLoader:
    def __init__(self, taxonomy_path: str) -> None:
        self.taxonomy_path = Path(taxonomy_path)

    def load(self) -> list[TaxonomyNode]:
        data = json.loads(self.taxonomy_path.read_text())
        nodes: list[TaxonomyNode] = []
        for item in data:
            nodes.append(
                TaxonomyNode(
                    code=str(item["code"]),
                    name=str(item["name"]),
                    keywords=tuple(item.get("keywords", [])),
                )
            )
        return nodes


class TaxonomyMapper:
    """Maps intent to taxonomy using model-first inference with keyword fallback."""

    def __init__(self, model: OpenAIChatCompletionsModel, nodes: list[TaxonomyNode]) -> None:
        self.model = model
        self.nodes = nodes

    def map(self, intent: StructuredIntent, top_k: int = 3) -> list[dict[str, str | float]]:
        candidates = self.model.infer_unspsc_candidates(intent.raw_input, top_k=top_k)
        if candidates:
            return [{"code": c.code, "name": c.name, "confidence": c.confidence} for c in candidates[:top_k]]

        lowered = intent.raw_input.lower()
        fallback: list[dict[str, str | float]] = []
        for node in self.nodes:
            if any(keyword.lower() in lowered for keyword in node.keywords):
                fallback.append({"code": node.code, "name": node.name, "confidence": 0.35})
        return fallback[:top_k]
