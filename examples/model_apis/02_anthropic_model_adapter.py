import json
import os
from typing import Any

from neoxlink_sdk import HeuristicModelAdapter, MatchCandidate, NormalizedIntent, ParsedIntent, UNSPSCCandidate


def _safe_json_dict(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except Exception:
        return {}


class AnthropicModelAdapter:
    provider_name = "anthropic"
    model_name = "claude-3-5-haiku-latest"

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-haiku-latest") -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model_name = model
        self._fallback = HeuristicModelAdapter()

    def _message_json(self, prompt: str) -> dict[str, Any]:
        if not self.api_key:
            return {}
        try:
            from anthropic import Anthropic
        except Exception:
            return {}
        client = Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model_name,
            max_tokens=700,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        text_block = ""
        if response.content:
            first = response.content[0]
            text_block = getattr(first, "text", "")
        return _safe_json_dict(text_block)

    def parse_intent(self, text: str) -> ParsedIntent:
        prompt = (
            "Return strict JSON with keys: "
            "product_or_service,constraints,quantity_signal,location,budget_hint,temporal_context,"
            "ambiguity_signals,confidence,raw_text. Input text: "
            f"{text}"
        )
        data = self._message_json(prompt)
        if not data:
            return self._fallback.parse_intent(text)
        data.setdefault("raw_text", text)
        return ParsedIntent.model_validate(data)

    def infer_unspsc_candidates(self, text: str, top_k: int = 5) -> list[UNSPSCCandidate]:
        return self._fallback.infer_unspsc_candidates(text, top_k=top_k)

    def score_match(self, normalized_intent: NormalizedIntent, candidate: MatchCandidate) -> dict[str, float]:
        return self._fallback.score_match(normalized_intent, candidate)


if __name__ == "__main__":
    print("Tip: pip install anthropic")
    adapter = AnthropicModelAdapter()
    parsed = adapter.parse_intent("Need business compliance advisor in Shanghai")
    print(parsed.model_dump())
