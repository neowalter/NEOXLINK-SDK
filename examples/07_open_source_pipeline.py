from neoxlink_sdk import OpenAIChatCompletionsModel
from neoxlink_sdk.open_source import (
    ExtractionEngine,
    IntentParser,
    MatchingEngine,
    ProviderSchema,
    TaxonomyLoader,
    TaxonomyMapper,
)


def main() -> None:
    model = OpenAIChatCompletionsModel(
        model="YOUR_MODEL_NAME",
        base_url="YOUR_OPENAI_COMPATIBLE_BASE_URL",
        api_key="YOUR_API_KEY",
    )

    parser = IntentParser(model=model)
    taxonomy_nodes = TaxonomyLoader("taxonomy/unspsc_open_source.json").load()
    mapper = TaxonomyMapper(model=model, nodes=taxonomy_nodes)
    extraction = ExtractionEngine(intent_parser=parser, taxonomy_mapper=mapper)
    matching = MatchingEngine(model=model)

    request = extraction.extract(
        request_id="req-001",
        text="Need startup policy consulting advisor in Shanghai.",
        entry_kind="demand",
    )

    providers = [
        ProviderSchema(
            provider_id="sup-001",
            name="Shanghai Policy Advisory",
            description="Startup compliance and policy consulting support.",
            categories=["80101500"],
            location="Shanghai",
            public_source_ref="https://example.com/provider/sup-001",
        )
    ]
    matches = matching.match(request=request, providers=providers, top_k=3)
    print(request.model_dump())
    print([item.model_dump() for item in matches])


if __name__ == "__main__":
    main()
