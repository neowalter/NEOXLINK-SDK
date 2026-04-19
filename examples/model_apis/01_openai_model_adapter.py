from neoxlink_sdk import OpenAIChatCompletionsModel


if __name__ == "__main__":
    print("Tip: pip install openai")
    try:
        from openai import AsyncOpenAI

        adapter = OpenAIChatCompletionsModel(
            model="YOUR_MODEL_NAME",
            openai_client=AsyncOpenAI(base_url="YOUR_OPENAI_COMPATIBLE_BASE_URL", api_key="YOUR_API_KEY"),
        )
    except Exception:
        adapter = OpenAIChatCompletionsModel(model="YOUR_MODEL_NAME")
    parsed = adapter.parse_intent("Need packaging materials supplier in Shenzhen under 5000 USD")
    print(parsed.model_dump())
