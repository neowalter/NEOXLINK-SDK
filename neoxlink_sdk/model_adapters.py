from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import threading
import time
from typing import Any, Final

from .catalog import CATALOG, UNSPSCEntry
from .engine import HeuristicModelAdapter
from .models import MatchCandidate, NormalizedIntent, ParsedIntent, UNSPSCCandidate

_CATALOG_BY_CODE: Final[dict[str, UNSPSCEntry]] = {e.code: e for e in CATALOG}
_UNSPSC_OPTIONS_JSON: Final[str] = json.dumps([{"code": e.code, "name": e.name} for e in CATALOG])

logger = logging.getLogger(__name__)


def _safe_json_dict(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except Exception as exc:
        preview = content[:240].replace("\n", " ")
        logger.warning("Failed to parse model JSON output: %s | preview=%r", exc, preview)
        print(f"[Model][WARN] Failed to parse JSON response: {exc}", flush=True)
        return {}


def _resolve_maybe_awaitable(value: Any) -> Any:
    if not inspect.isawaitable(value):
        return value
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(value)

    result: dict[str, Any] = {}
    error: dict[str, BaseException] = {}

    def _runner() -> None:
        try:
            result["value"] = asyncio.run(value)
        except BaseException as exc:  # pragma: no cover
            error["exc"] = exc

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join()
    if "exc" in error:
        raise error["exc"]
    return result.get("value")


class OpenAIChatCompletionsModel:
    """Model adapter for OpenAI-compatible chat completion endpoints.

    Supports either:
    - `openai.OpenAI(...)`
    - `openai.AsyncOpenAI(...)`
    - any OpenAI-compatible provider via custom `base_url` and `model`
    """

    provider_name = "openai-compatible"

    def __init__(
        self,
        *,
        model: str,
        openai_client: Any | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        provider_name: str = "openai-compatible",
        stream_output: bool = False,
        debug_steps: bool = False,
    ) -> None:
        self.model_name = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.openai_client = openai_client
        self.provider_name = provider_name
        self.stream_output = stream_output
        self.debug_steps = debug_steps
        self._fallback = HeuristicModelAdapter()

    @classmethod
    def for_openai(cls, model: str, api_key: str | None = None) -> "OpenAIChatCompletionsModel":
        return cls(model=model, api_key=api_key, provider_name="openai")

    @classmethod
    def for_openrouter(
        cls,
        model: str,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
    ) -> "OpenAIChatCompletionsModel":
        return cls(
            model=model,
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            base_url=base_url,
            provider_name="openrouter",
        )

    @classmethod
    def for_local(
        cls,
        model: str,
        base_url: str = "http://localhost:11434/v1",
        api_key: str | None = None,
    ) -> "OpenAIChatCompletionsModel":
        return cls(model=model, api_key=api_key or "local", base_url=base_url, provider_name="local-openai-compatible")

    def _build_client(self) -> Any | None:
        if self.openai_client is not None:
            return self.openai_client
        try:
            from openai import OpenAI
        except Exception:
            return None
        if not self.api_key and not self.base_url:
            return None
        return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _chat_json(self, prompt: str) -> dict[str, Any]:
        client = self._build_client()
        if client is None:
            if self.debug_steps:
                print("[Model] OpenAI-compatible client unavailable; returning empty JSON.", flush=True)
            logger.error(
                "OpenAI-compatible client unavailable (provider=%s, model=%s).",
                self.provider_name,
                self.model_name,
            )
            return {}
        if self.debug_steps:
            print(
                f"[Model] Request started ({self.provider_name}/{self.model_name}).",
                flush=True,
            )
        logger.info("Model request started (provider=%s, model=%s).", self.provider_name, self.model_name)
        started = time.perf_counter()
        request_kwargs: dict[str, Any] = {
            "model": self.model_name,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "Return strict JSON only."},
                {"role": "user", "content": prompt},
            ],
        }

        content = ""
        try:
            if self.stream_output:
                request_kwargs["stream"] = True
                try:
                    stream = _resolve_maybe_awaitable(client.chat.completions.create(**request_kwargs))
                    if self.debug_steps:
                        print("[Model] Streaming response:", flush=True)
                    chunks: list[str] = []
                    for chunk in stream:
                        piece = ""
                        try:
                            piece = chunk.choices[0].delta.content or ""
                        except Exception:
                            piece = ""
                        if piece:
                            print(piece, end="", flush=True)
                            chunks.append(piece)
                    if chunks:
                        print("", flush=True)
                    content = "".join(chunks)
                except TypeError:
                    # Some compatible clients do not accept the `stream` argument.
                    request_kwargs.pop("stream", None)
                    if self.debug_steps:
                        print(
                            "[Model] Streaming unsupported by client; falling back to non-stream response.",
                            flush=True,
                        )
                    response = _resolve_maybe_awaitable(client.chat.completions.create(**request_kwargs))
                    content = response.choices[0].message.content or ""
            else:
                response = _resolve_maybe_awaitable(client.chat.completions.create(**request_kwargs))
                content = response.choices[0].message.content or ""
        except Exception as exc:
            print(f"[Model][ERROR] Request failed: {exc}", flush=True)
            logger.exception(
                "Model request failed (provider=%s, model=%s).",
                self.provider_name,
                self.model_name,
            )
            return {}

        if self.debug_steps:
            elapsed = time.perf_counter() - started
            print(f"[Model] Request completed in {elapsed:.2f}s.", flush=True)
        logger.info(
            "Model request completed (provider=%s, model=%s, elapsed=%.2fs).",
            self.provider_name,
            self.model_name,
            time.perf_counter() - started,
        )
        return _safe_json_dict(content)

    def analyze_json(self, prompt: str) -> dict[str, Any]:
        """Public utility for structured reasoning tasks.

        Use this for clarification planning, sufficiency checks, and other
        JSON-constrained analysis steps.
        """
        return self._chat_json(prompt)

    def parse_intent(self, text: str) -> ParsedIntent:
        prompt = (
            "Analyze procurement intent from user input. Think carefully and return JSON only.\n"
            "Schema keys: product_or_service,constraints,quantity_signal,location,budget_hint,"
            "temporal_context,ambiguity_signals,confidence,raw_text.\n"
            f"Input: {text}"
        )
        data = self._chat_json(prompt)
        if not data:
            return self._fallback.parse_intent(text)
        data.setdefault("raw_text", text)
        return ParsedIntent.model_validate(data)

    def infer_unspsc_candidates(self, text: str, top_k: int = 5) -> list[UNSPSCCandidate]:
        prompt = (
            "Infer the top UNSPSC candidates for the procurement intent below. "
            "Return JSON only with key `candidates`.\n"
            "Each candidate item must include: code,name,confidence.\n"
            f"Intent: {text}\n"
            f"Options: {_UNSPSC_OPTIONS_JSON}"
        )
        payload = self._chat_json(prompt)
        ranked_items = payload.get("candidates")
        if not isinstance(ranked_items, list):
            return self._fallback.infer_unspsc_candidates(text, top_k=top_k)

        inferred: list[UNSPSCCandidate] = []
        for item in ranked_items:
            if not isinstance(item, dict):
                continue
            code = str(item.get("code", ""))
            if code not in _CATALOG_BY_CODE:
                continue
            base = _CATALOG_BY_CODE[code]
            confidence_raw = item.get("confidence", 0.5)
            try:
                confidence = float(confidence_raw)
            except (TypeError, ValueError):
                confidence = 0.5
            inferred.append(
                UNSPSCCandidate(
                    code=code,
                    name=str(item.get("name", base.name)),
                    confidence=min(1.0, max(0.0, confidence)),
                )
            )
        if not inferred:
            return self._fallback.infer_unspsc_candidates(text, top_k=top_k)
        inferred.sort(key=lambda c: c.confidence, reverse=True)
        return inferred[: max(1, top_k)]

    def score_match(self, normalized_intent: NormalizedIntent, candidate: MatchCandidate) -> dict[str, float]:
        return self._fallback.score_match(normalized_intent, candidate)


# Backward-compatible alias for previous public name.
OpenAICompatibleModelAdapter = OpenAIChatCompletionsModel
