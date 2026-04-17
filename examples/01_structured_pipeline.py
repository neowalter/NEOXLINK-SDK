from neoxlink_sdk import NeoXlinkClient, StructuredSubmissionPipeline


def main() -> None:
    client = NeoXlinkClient(base_url="https://neoxailink.com", api_key="ak_live_xxx")
    pipeline = StructuredSubmissionPipeline(client)

    draft = pipeline.parse(
        text="Need a startup advisor for policy and subsidy support in Wuhan.",
        entry_kind="demand",
        metadata={"channel": "sdk-example"},
    )
    print("UNSPSC:", draft.preview.unspsc)

    confirmed = pipeline.confirm(draft=draft)
    print("Raw Entry ID:", confirmed.raw_entry_id)

    resolved = pipeline.resolve(confirmed.raw_entry_id)
    print("Resolve Path:", resolved.path)


if __name__ == "__main__":
    main()
