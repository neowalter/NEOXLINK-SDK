import json
import os
from typing import Any

from neoxlink_sdk import HeuristicModelAdapter, MatchCandidate, NormalizedIntent, ParsedIntent, UNSPSCCandidate


def _safe_json_dict(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except Exception:
        return {}


class GeminiModelAdapter:
    provider_name = "google"
    model_name = "gemini-1.5-flash"

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash") -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model
        self._fallback = HeuristicModelAdapter()

    def _generate_json(self, prompt: str) -> dict[str, Any]:
        if not self.api_key:
            return {}
        try:
            from google import genai
        except Exception:
            return {}
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=f"Return strict JSON only.\n{prompt}",
        )
        text = getattr(response, "text", "") or ""
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
    print("Tip: pip install google-genai")
    adapter = GeminiModelAdapter()
    parsed = adapter.parse_intent("Need internet platform development partner in Guangzhou")
    print(parsed.model_dump())
