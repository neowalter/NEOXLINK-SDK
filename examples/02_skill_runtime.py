from neoxlink_sdk import (
    NeoXlinkClient,
    NeoxlinkSkill,
    SkillRequest,
    StructuredSubmissionPipeline,
)


def main() -> None:
    skill = NeoxlinkSkill(
        StructuredSubmissionPipeline(
            NeoXlinkClient(base_url="https://neoxailink.com", api_key="ak_live_xxx")
        )
    )

    preview = skill.run(
        SkillRequest(
            text="Offer policy-compliance consulting for early-stage AI startups.",
            entry_kind="supply",
            auto_confirm=False,
        )
    )
    print("Preview status:", preview.status)
    print("Preview UNSPSC:", preview.draft.preview.unspsc)

    confirmed = skill.run(
        SkillRequest(
            text="Need enterprise packaging and logistics support in Shenzhen.",
            entry_kind="demand",
            auto_confirm=True,
            overrides={"constraints": {"region": ["Shenzhen"]}},
            use_own_model=True,
        )
    )
    print("Confirmed status:", confirmed.status)
    print("Confirmed entry:", confirmed.confirmed.raw_entry_id if confirmed.confirmed else None)


if __name__ == "__main__":
    main()
