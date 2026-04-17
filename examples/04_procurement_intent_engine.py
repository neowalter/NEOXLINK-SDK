from neoxlink_sdk import InMemoryDataSource, MatchCandidate, ProcurementIntentEngine


def main() -> None:
    records = [
        MatchCandidate(
            partner_id="sup-001",
            partner_type="supplier",
            title="Shanghai Policy Advisory Group",
            description="Startup compliance and policy support for market entry.",
            unspsc_codes=["80101500"],
            location="Shanghai",
            recency_days=12,
            performance_score=0.91,
            attributes={"domain": "startup_policy"},
        ),
        MatchCandidate(
            partner_id="sup-002",
            partner_type="supplier",
            title="GrowthFly Marketing Studio",
            description="Digital campaign planning and lead generation.",
            unspsc_codes=["80141600"],
            location="Shenzhen",
            recency_days=28,
            performance_score=0.84,
            attributes={"domain": "performance_marketing"},
        ),
    ]

    engine = ProcurementIntentEngine(data_source=InMemoryDataSource(records))
    result = engine.run(
        text="Need startup policy advisor in Shanghai for urgent launch support.",
        entry_kind="demand",
        target="suppliers",
        top_k=3,
        clarification_answers={"quantity": "project-based"},
    )

    print("UNSPSC:", result.normalized_intent.unspsc_code, result.normalized_intent.unspsc_name)
    for item in result.matches:
        print(item.partner_id, f"score={item.score:.3f}", item.reason_signals)


if __name__ == "__main__":
    main()
