# Deprecated / archival tree

This directory holds **non-shipping** material that was removed from the active package layout to avoid confusion with `neoxlink_sdk/`.

## `core/`

Historical **Pydantic v1-style** schema helpers (`StructuredRecordV1`, dedup hashes, `MatchFeatures`) that were **never imported** by `neoxlink_sdk`, `neoxlink`, tests, or examples. The shipping SDK uses `neoxlink_sdk.models` and related modules instead.

If you still need these types, copy the subtree or import from a pinned commit; they are not installed via `pip install neoxlink`.
