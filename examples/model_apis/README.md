# Model API Integration Examples

This folder demonstrates how to connect multiple model providers to the
`ProcurementIntentEngine` model adapter contract.

## Recommended default (simple path)

Use `OpenAIChatCompletionsModel` first. It works with OpenAI and any
OpenAI-compatible endpoint by changing only `model` and `base_url`.

## 5-minute quick demo (MVU path)

```bash
pip install -e .
python examples/model_apis/01_openai_model_adapter.py
```

Use this as the default method: `OpenAIChatCompletionsModel` supports different
models/providers through the same interface by changing `model`, `base_url`, or `openai_client`.

```python
from openai import AsyncOpenAI
from neoxlink_sdk import OpenAIChatCompletionsModel

model = OpenAIChatCompletionsModel(
    model="qwen2.5:7b",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="local"),
)
```

## Included examples

- `01_openai_model_adapter.py` - default OpenAI-compatible path
- `05_model_router_adapter.py` - dynamic routing on top of default path
- `02_anthropic_model_adapter.py` - advanced provider-specific example
- `03_gemini_model_adapter.py` - advanced provider-specific example
- `04_ollama_model_adapter.py` - advanced provider-specific example

## Environment variables

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `OPENROUTER_API_KEY` (if using OpenRouter via OpenAI-compatible path)
- `OLLAMA_BASE_URL` (optional, defaults to `http://localhost:11434`)

## Notes

- Each adapter falls back to deterministic local heuristics if credentials are
  missing or provider calls fail.
- The examples are intentionally minimal and can be copied into production
  plugin modules.
