from neoxlink_sdk import NeoXlinkClient, NeoxlinkSubmissionChain, StructuredSubmissionPipeline


def main() -> None:
    chain = NeoxlinkSubmissionChain(
        StructuredSubmissionPipeline(
            NeoXlinkClient(base_url="https://neoxailink.com", api_key="ak_live_xxx")
        )
    )

    result = chain.invoke(
        {
            "text": "Need growth consulting for B2B SaaS launch in East China.",
            "entry_kind": "demand",
            "metadata": {"channel": "chain-example"},
            "auto_confirm": True,
            "resolve_after_confirm": True,
        }
    )
    print(result.model_dump(mode="json"))


if __name__ == "__main__":
    main()
