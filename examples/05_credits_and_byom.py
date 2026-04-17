from neoxlink_sdk import CreditLedger, MeteredNeoXlinkClient, StructuredSubmissionPipeline


def main() -> None:
    ledger = CreditLedger()
    account = ledger.ensure_account("user_free_demo", tier="free", starting_credits=20)
    print("Initial account:", account.model_dump())

    client = MeteredNeoXlinkClient(
        user_id="user_free_demo",
        ledger=ledger,
        base_url="https://neoxailink.com",
        api_key="ak_live_xxx",
    )
    pipeline = StructuredSubmissionPipeline(client)

    # Free users get 5 LLM extraction submits/day without credit debit.
    for idx in range(1, 6):
        pipeline.parse(
            text=f"Need startup legal advisor #{idx}",
            entry_kind="demand",
            metadata={"channel": "credits-example"},
        )

    after_free_quota = ledger.get_account("user_free_demo")
    print("After 5 free extractions:", after_free_quota.model_dump())

    # 6th extraction uses paid credits (llm_extraction_credit_cost).
    pipeline.parse(
        text="Need policy grant consultant #6",
        entry_kind="demand",
        metadata={"channel": "credits-example"},
    )
    after_paid_extraction = ledger.get_account("user_free_demo")
    print("After 6th extraction:", after_paid_extraction.model_dump())

    # BYOM mode: no additional extraction credit charge.
    pipeline.parse(
        text="Need advisor but using my own model endpoint",
        entry_kind="demand",
        metadata={"channel": "credits-example"},
        use_own_model=True,
    )
    after_byom = ledger.get_account("user_free_demo")
    print("After BYOM extraction:", after_byom.model_dump())

    # Search + matching consume credits.
    client.search(query="startup advisor in Shanghai", entry_kind="supply", top_k=10)
    after_search = ledger.get_account("user_free_demo")
    print("After search+matching:", after_search.model_dump())


if __name__ == "__main__":
    main()
