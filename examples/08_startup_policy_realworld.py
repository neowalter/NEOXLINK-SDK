import os
from types import SimpleNamespace
import json
import logging
import httpx

from neoxlink_sdk import OpenAIChatCompletionsModel
from neoxlink_sdk.open_source import StartupPolicyAdvisor


class _QwenCompletionsProxy:
    def __init__(self, *, api_key: str, base_url: str) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    def create(self, **kwargs):
        stream = bool(kwargs.pop("stream", False))
        extra_body = dict(kwargs.pop("extra_body", {}) or {})
        extra_body["enable_thinking"] = True
        extra_body["enable_search"] = True
        payload = {**kwargs, **extra_body}
        url = f"{self._base_url}/chat/completions"
        try:
            timeout = httpx.Timeout(connect=8.0, read=20.0, write=20.0, pool=20.0)
            with httpx.Client(timeout=timeout, trust_env=False) as client:
                response = client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    content=json.dumps(payload).encode("utf-8"),
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise RuntimeError(f"DashScope API error: {exc.response.status_code} {detail}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"DashScope network error: {exc}. Check your network/proxy/firewall and DashScope region access."
            ) from exc

        content = data["choices"][0]["message"].get("content", "")
        if stream:
            chunk_size = 24
            chunks: list[SimpleNamespace] = []
            for idx in range(0, len(content), chunk_size):
                piece = content[idx : idx + chunk_size]
                chunks.append(
                    SimpleNamespace(
                        choices=[SimpleNamespace(delta=SimpleNamespace(content=piece))]
                    )
                )
            return chunks
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )


class _QwenChatProxy:
    def __init__(self, *, api_key: str, base_url: str) -> None:
        self.completions = _QwenCompletionsProxy(api_key=api_key, base_url=base_url)


class _QwenOpenAIClientProxy:
    def __init__(self, *, api_key: str) -> None:
        self.chat = _QwenChatProxy(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    # Qwen official API (DashScope OpenAI-compatible endpoint).
    # Uses latest high-performance model and enables built-in thinking + web search.
    api_key = os.getenv("DASHSCOPE_API_KEY", "")
    if not api_key:
        raise RuntimeError("Please set DASHSCOPE_API_KEY before running this example.")

    qwen_client = _QwenOpenAIClientProxy(api_key=api_key)
    model = OpenAIChatCompletionsModel(
        model="qwen-max-latest",
        openai_client=qwen_client,
        provider_name="qwen-dashscope",
        stream_output=True,
        debug_steps=True,
    )

    advisor = StartupPolicyAdvisor(model=model)
    advisor.run_interactive("我想找武汉的创业咨询服务")


if __name__ == "__main__":
    main()
