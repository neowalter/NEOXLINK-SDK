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
- structured procurement intent to demand/supply matching

## Install

```bash
pip install -e .
```

## Design Principles

- **Natural-language first**: every core entry point accepts free text.
- **Structured-by-default**: parse outputs are typed and include UNSPSC standardization.
- **Composable runtime**: direct API client, pipeline orchestration, skill adapter, and MCP adapter.
- **Professional operator ergonomics**: concise models, explicit stages, and predictable return payloads.

## Architecture (v0.4)

## Structured Matching Engine (v0.3)

The SDK now ships a staged `ProcurementIntentEngine` for controllable demand/supply matching:

1. Intent parsing from fragmented natural language
2. UNSPSC mapping with top candidate confidence list
3. Clarification loop trigger + targeted questions
4. Structured normalization into canonical query object
5. Hybrid retrieval from pluggable data source
6. Deterministic ranking with explanation signals

This is intentionally model/provider agnostic through a `ModelAdapter` interface and supports
pluggable connectors through a `DataSource` interface.

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

### `neoxlink_sdk.credits` (Credit + BYOM Control)

Credit layer for product billing rules:

- every search and matching operation consumes credits
- free tier gets `5` LLM extraction submits/day at zero cost
- BYOM mode (`use_own_model=True`) skips platform extraction charge
- `MeteredNeoXlinkClient` integrates billing enforcement with standard SDK calls

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

## Credits, Free Quota, and BYOM

```python
from neoxlink_sdk import CreditLedger, MeteredNeoXlinkClient, StructuredSubmissionPipeline

ledger = CreditLedger()
ledger.ensure_account("user_001", tier="free", starting_credits=30)

client = MeteredNeoXlinkClient(
    user_id="user_001",
    ledger=ledger,
    base_url="https://neoxailink.com",
    api_key="ak_live_xxx",
)
pipeline = StructuredSubmissionPipeline(client)

# Free user: first 5 extraction submits/day are free.
pipeline.parse("Need startup advisor in Shanghai", entry_kind="demand")

# BYOM: use your own model/API stack, skip extraction charge.
pipeline.parse(
    "Need startup advisor; route extraction via my own model endpoint",
    entry_kind="demand",
    use_own_model=True,
)

# Search + matching consume credits.
client.search(query="startup advisor in Shanghai", entry_kind="supply")
```

## Quick Start: Procurement Intent Engine

```python
from neoxlink_sdk import InMemoryDataSource, MatchCandidate, ProcurementIntentEngine

records = [
    MatchCandidate(
        partner_id="sup-001",
        partner_type="supplier",
        title="Shanghai Policy Advisory Group",
        description="Startup compliance and policy support for market entry.",
        unspsc_codes=["80101500"],
        location="Shanghai",
        performance_score=0.91,
    ),
]

engine = ProcurementIntentEngine(data_source=InMemoryDataSource(records))
result = engine.run(
    text="Need startup policy advisor in Shanghai for urgent launch support.",
    entry_kind="demand",
    target="suppliers",
    top_k=3,
)

print(result.normalized_intent.model_dump())
print([m.model_dump() for m in result.matches])
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
    {
        "text": "Need startup advisor in Shenzhen",
        "entry_kind": "demand",
        "use_own_model": True,
    },
)

submit_result = adapter.call_tool(
    "neoxlink.confirmed_submit",
    {
        "text": "Need startup advisor in Shenzhen",
        "entry_kind": "demand",
        "overrides": {"constraints": {"region": ["Shenzhen"]}},
        "use_own_model": False,
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

If you need candidate list retrieval for disambiguation:

```python
from neoxlink_sdk import unspsc_candidates

for entry, score in unspsc_candidates("Need growth marketing campaign support", top_k=3):
    print(entry.code, entry.name, score)
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
- `examples/04_procurement_intent_engine.py` - staged UNSPSC matching engine
- `examples/05_credits_and_byom.py` - credit metering and free-tier quota

## License

MIT
