"""Template: custom connector/data source plugin."""

from neoxlink_sdk import MatchCandidate, NormalizedIntent


class CustomDataSource:
    source_name = "custom_connector"

    def __init__(self) -> None:
        # TODO: initialize db/client credentials.
        pass

    def search(self, normalized_intent: NormalizedIntent, target: str, limit: int) -> list[MatchCandidate]:
        # TODO: implement hybrid retrieval (structured filter + semantic index).
        # Return MatchCandidate entries that fit the intent.
        _ = (normalized_intent, target, limit)
        return []
