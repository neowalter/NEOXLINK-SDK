import json
import os
from typing import Any

from neoxlink_sdk import HeuristicModelAdapter, MatchCandidate, NormalizedIntent, ParsedIntent, UNSPSCCandidate


def _safe_json_dict(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except Exception:
        return {}


class OllamaModelAdapter:
    provider_name = "ollama"
    model_name = "llama3.1:8b"

    def __init__(self, base_url: str | None = None, model: str = "llama3.1:8b") -> None:
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = model
        self._fallback = HeuristicModelAdapter()

    def _generate_json(self, prompt: str) -> dict[str, Any]:
        try:
            import ollama
        except Exception:
            return {}
        client = ollama.Client(host=self.base_url)
        response = client.generate(
            model=self.model_name,
            prompt=f"Return strict JSON only.\n{prompt}",
            options={"temperature": 0},
        )
        text = response.get("response", "")
        return _safe_json_dict(text)

    def parse_intent(self, text: str) -> ParsedIntent:
        prompt = (
            "Extract procurement intent JSON with keys: "
            "product_or_service,constraints,quantity_signal,location,budget_hint,temporal_context,"
            "ambiguity_signals,confidence,raw_text. Input: "
            f"{text}"
        )
        data = self._generate_json(prompt)
        if not data:
            return self._fallback.parse_intent(text)
        data.setdefault("raw_text", text)
        return ParsedIntent.model_validate(data)

    def infer_unspsc_candidates(self, text: str, top_k: int = 5) -> list[UNSPSCCandidate]:
        return self._fallback.infer_unspsc_candidates(text, top_k=top_k)

    def score_match(self, normalized_intent: NormalizedIntent, candidate: MatchCandidate) -> dict[str, float]:
        return self._fallback.score_match(normalized_intent, candidate)


if __name__ == "__main__":
    print("Tip: pip install ollama")
    adapter = OllamaModelAdapter()
    parsed = adapter.parse_intent("Need software development outsourcing for B2B SaaS web app")
    print(parsed.model_dump())
