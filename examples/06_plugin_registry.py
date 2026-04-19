from neoxlink_sdk import (
    InMemoryDataSource,
    MatchCandidate,
    PluginRegistry,
    ProcurementIntentEngine,
    default_ranking_strategy,
)


def recency_heavy_ranking(signals, intent, candidate):
    baseline = default_ranking_strategy(signals, intent, candidate)
    return min(1.0, max(0.0, (baseline * 0.8) + (signals["recency"] * 0.2)))


def main() -> None:
    registry = PluginRegistry()

    registry.register_data_source(
        "demo_memory",
        lambda: InMemoryDataSource(
            [
                MatchCandidate(
                    partner_id="sup-001",
                    partner_type="supplier",
                    title="Fast Policy Advisory",
                    description="Startup policy and compliance consultancy.",
                    unspsc_codes=["80101500"],
                    location="Shanghai",
                    performance_score=0.9,
                    recency_days=8,
                ),
                MatchCandidate(
                    partner_id="sup-002",
                    partner_type="supplier",
                    title="General Business Consulting",
                    description="Corporate advisory and market-entry support.",
                    unspsc_codes=["80101500"],
                    location="Shanghai",
                    performance_score=0.8,
                    recency_days=60,
                ),
            ]
        ),
    )
    registry.register_ranking_strategy("recency_heavy", lambda: recency_heavy_ranking)

    data_source = registry.create_data_source("demo_memory")
    ranking_strategy = registry.create_ranking_strategy("recency_heavy")
    engine = ProcurementIntentEngine(data_source=data_source, ranking_strategy=ranking_strategy)

    result = engine.run(
        text="Need urgent startup policy advisor in Shanghai",
        entry_kind="demand",
        target="suppliers",
    )
    print(result.matches[0].model_dump())


if __name__ == "__main__":
    main()
