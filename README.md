# neoxlink-sdk

Public Python SDK for `neoxailink.com` demand/supply workflows.

This SDK now supports a full structured flow:

1. User submits natural language text
2. Backend LLM parses and refines into structured preview
3. User (or agent) confirms/edit overrides
4. Record is confirmed into structured data
5. Optional resolve step (AI-direct or fallback guidance)

UNSPSC is used as the normalization standard for both needs (demand) and
solutions (supply), using standard code + name pairs.

It is designed for:

- direct app/backend integrations
- Skill-style runtimes
- MCP-style tool exposure

## Install

```bash
pip install -e .
```

## Design Principles

- **Natural-language first**: every core entry point accepts free text.
- **Structured-by-default**: parse outputs are typed and include UNSPSC standardization.
- **Composable runtime**: direct API client, pipeline orchestration, skill adapter, and MCP adapter.
- **Professional operator ergonomics**: concise models, explicit stages, and predictable return payloads.

## Architecture (v0.2)

### `neoxlink_sdk.client.NeoXlinkClient`

HTTP layer for `neoxailink.com` APIs, including:

- `parse_entry()`
- `confirm_entry()`
- `resolve_entry()`
- `structured_submit()` (parse + confirm)
- plus legacy methods: `submit_entry()`, `get_entry()`, `search()`

### `neoxlink_sdk.pipeline.StructuredSubmissionPipeline`

Orchestration layer for parse -> confirm -> resolve with explicit state objects:

- `ParseDraft`
- `ConfirmedEntry`
- `ResolveResult`
- `PipelineOutcome`
- built-in UNSPSC classification enrichment (`code` + `name`)

### `neoxlink_sdk.chains.NeoxlinkSubmissionChain`

LangChain-like invocation style (`invoke`) for orchestration-heavy applications.

### `neoxlink_sdk.skill.NeoxlinkSkill`

Skill adapter around the pipeline:

- return preview-only for user confirmation
- or auto-confirm and return full outcome

### `neoxlink_sdk.mcp.NeoxlinkMCPAdapter`

MCP-friendly tool facade with two tool methods:

- `neoxlink.parse_preview`
- `neoxlink.confirmed_submit`

---

## Quick Start: Structured Workflow

```python
from neoxlink_sdk import NeoXlinkClient, StructuredSubmissionPipeline

client = NeoXlinkClient(
    base_url="https://neoxailink.com",
    api_key="ak_live_xxx",
)
pipeline = StructuredSubmissionPipeline(client)

# 1) parse/preview (LLM-refined structure)
draft = pipeline.parse(
    text="I need a startup advisor for policy support in Shanghai.",
    entry_kind="demand",
    metadata={"channel": "sdk"},
)
print(draft.preview.unspsc.code, draft.preview.unspsc.name)

# 2) user confirms (optional overrides)
confirmed = pipeline.confirm(
    draft=draft,
    overrides={"constraints": {"region": ["Shanghai"]}},
)

# 3) optional resolve
resolved = pipeline.resolve(confirmed.raw_entry_id)
print(resolved.path, resolved.reason)
```

## Chain-Style Usage (LangChain-like)

```python
from neoxlink_sdk import NeoXlinkClient, NeoxlinkSubmissionChain, StructuredSubmissionPipeline

chain = NeoxlinkSubmissionChain(
    StructuredSubmissionPipeline(
        NeoXlinkClient(base_url="https://neoxailink.com", api_key="ak_live_xxx")
    )
)

outcome = chain.invoke(
    {
        "text": "Need startup policy compliance advisor in Shanghai.",
        "entry_kind": "demand",
        "auto_confirm": True,
        "resolve_after_confirm": True,
    }
)
print(outcome.model_dump(mode="json"))
```

## Skill Integration Example

```python
from neoxlink_sdk import (
    NeoXlinkClient,
    NeoxlinkSkill,
    SkillRequest,
    StructuredSubmissionPipeline,
)

skill = NeoxlinkSkill(
    StructuredSubmissionPipeline(
        NeoXlinkClient(base_url="https://neoxailink.com", api_key="ak_live_xxx")
    )
)

# Preview-first mode (human confirmation loop)
preview = skill.run(
    SkillRequest(
        text="Offer enterprise packaging optimization consulting.",
        entry_kind="supply",
        auto_confirm=False,
    )
)
print(preview.status)  # preview_ready

# Auto-confirm mode
final = skill.run(
    SkillRequest(
        text="Need AI policy advisory for startup launch.",
        entry_kind="demand",
        auto_confirm=True,
        overrides={"category": "consulting"},
    )
)
print(final.status)  # confirmed
```

## MCP Integration Example

```python
from neoxlink_sdk import (
    NeoXlinkClient,
    NeoxlinkMCPAdapter,
    NeoxlinkSkill,
    StructuredSubmissionPipeline,
)

adapter = NeoxlinkMCPAdapter(
    NeoxlinkSkill(
        StructuredSubmissionPipeline(
            NeoXlinkClient(base_url="https://neoxailink.com", api_key="ak_live_xxx")
        )
    )
)

tools = adapter.list_tools()
print([tool["name"] for tool in tools])

preview_result = adapter.call_tool(
    "neoxlink.parse_preview",
    {"text": "Need startup advisor in Shenzhen", "entry_kind": "demand"},
)

submit_result = adapter.call_tool(
    "neoxlink.confirmed_submit",
    {
        "text": "Need startup advisor in Shenzhen",
        "entry_kind": "demand",
        "overrides": {"constraints": {"region": ["Shenzhen"]}},
    },
)
```

## UNSPSC Standardization

The SDK classifies both demand and supply text into UNSPSC:

- during parse stage (`draft.preview.unspsc`)
- and forwards `unspsc_code` / `unspsc_name` in confirm overrides

If you need standalone classification:

```python
from neoxlink_sdk import classify_unspsc

code, name, confidence = classify_unspsc("Need startup policy consulting support")
print(code, name, confidence)
```

## Core Utilities

`core/` remains available for shared matching/dedup primitives:

- `core/schema.py`
- `core/dedup.py`
- `core/matching.py`

## Examples

- `examples/01_structured_pipeline.py` - parse/confirm/resolve flow
- `examples/02_skill_runtime.py` - skill runtime integration
- `examples/03_chain_style.py` - chain-style invocation

## License

MIT
