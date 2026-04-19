# neoxlink-sdk

Public Python SDK for `neoxailink.com` demand/supply workflows.

中文文档请见：[`README.zh-CN.md`](README.zh-CN.md)

This SDK now supports a full structured flow:

1. User submits natural language text
2. Backend LLM parses and refines into structured preview
3. User (or agent) confirms/edit overrides
4. Record is confirmed into structured data
5. Optional resolve step (AI-direct or fallback guidance)

## Problem -> Solution -> Quick Start (MVU)

**Problem:** fragmented natural-language procurement requests create noisy intake and weak supplier/buyer matching.

**Solution:** neoxlink-sdk standardizes requests into UNSPSC intent, runs clarification when needed, and returns ranked matches with transparent scoring signals.

**Quick Start (under 5 minutes):**

```bash
pip install -e .
python examples/04_procurement_intent_engine.py
```

Simplest OpenAI-compatible setup:

```python
from neoxlink_sdk import MatchCandidate, create_engine

engine = create_engine(
    records=[
        MatchCandidate(
            partner_id="sup-001",
            partner_type="supplier",
            title="Example supplier",
            description="Policy consulting support",
            unspsc_codes=["80101500"],
        )
    ],
    model="<your-model-name>",
    base_url="<your-openai-compatible-url>",
    api_key="<your-api-key-or-local-token>",
)
```

UNSPSC is used as the normalization standard for both needs (demand) and
solutions (supply), using standard code + name pairs.

It is designed for:

- direct app/backend integrations
- Skill-style runtimes
- MCP-style tool exposure
- structured procurement intent to demand/supply matching

## Open-Source Community Structure

This repository now follows a contributor-first structure:

1. [Templates](community/01_templates.md)
2. [Examples](community/02_examples.md)
3. [Plugins](community/03_plugins.md)
4. [Contributors](community/04_contributors.md)
5. [Ecosystem](community/05_ecosystem.md)
6. [Adoption](community/06_adoption.md)

## Open-Source Scope

- included/excluded boundaries: [`OPEN_SOURCE_SCOPE.md`](OPEN_SOURCE_SCOPE.md)
- repository module map: [`REPOSITORY_ARCHITECTURE.md`](REPOSITORY_ARCHITECTURE.md)
- contributor workflow: [`CONTRIBUTOR_WORKFLOW.md`](CONTRIBUTOR_WORKFLOW.md)
- data collaboration rules: [`DATA_COLLABORATION_GUIDELINES.md`](DATA_COLLABORATION_GUIDELINES.md)
- prompt collaboration process: [`PROMPT_COLLABORATION.md`](PROMPT_COLLABORATION.md)
- governance model: [`GOVERNANCE.md`](GOVERNANCE.md)

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

### `neoxlink_sdk.plugins.PluginRegistry`

Plugin registry for open-source extension points:

- register model adapters
- register data source connectors
- register ranking strategies
- instantiate plugins by name for runtime composition

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

## Skill Integration (Claude Code Style)

This SDK exposes a stable skill contract designed for Claude Code-style tool runtimes:

- Input object: `SkillRequest`
- Output object: `SkillResponse`
- Deterministic status values: `preview_ready`, `confirmed`, `skipped`
- Explicit human-in-the-loop switch: `auto_confirm=False`

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

# Claude Code-friendly: first pass returns preview for confirmation loop.
preview = skill.run(
    SkillRequest(
        text="Offer enterprise packaging optimization consulting.",
        entry_kind="supply",
        auto_confirm=False,
    )
)
print(preview.status)  # preview_ready

# Second pass confirms and optionally resolves.
confirmed = skill.run(
    SkillRequest(
        text="Need AI policy advisory for startup launch.",
        entry_kind="demand",
        auto_confirm=True,
        overrides={"category": "consulting"},
        resolve_after_confirm=True,
    )
)
print(confirmed.status)  # confirmed
```

## MCP Integration (Claude Code + OpenClaw)

### Quick install with OpenClaw

```bash
pip install neoxlink-sdk
# If OpenClaw is not installed yet:
pip install openclaw
```

### Claude Code standard MCP tool surface

`NeoxlinkMCPAdapter` keeps tool names stable and explicit:

- `neoxlink.parse_preview`
- `neoxlink.confirmed_submit`
- `neoxlink.match_intent` (when `ProcurementIntentEngine` is configured)

```python
from neoxlink_sdk import (
    InMemoryDataSource,
    MatchCandidate,
    NeoXlinkClient,
    NeoxlinkMCPAdapter,
    NeoxlinkSkill,
    ProcurementIntentEngine,
    StructuredSubmissionPipeline,
)

client = NeoXlinkClient(base_url="https://neoxailink.com", api_key="ak_live_xxx")
skill = NeoxlinkSkill(StructuredSubmissionPipeline(client))

engine = ProcurementIntentEngine(
    data_source=InMemoryDataSource(
        [
            MatchCandidate(
                partner_id="sup-001",
                partner_type="supplier",
                title="Shanghai Policy Advisory Group",
                description="Startup compliance and policy support.",
                unspsc_codes=["80101500"],
                location="Shanghai",
                performance_score=0.91,
            )
        ]
    )
)

adapter = NeoxlinkMCPAdapter(skill=skill, engine=engine)
print([tool["name"] for tool in adapter.list_tools()])

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

match_result = adapter.call_tool(
    "neoxlink.match_intent",
    {
        "text": "Need urgent startup policy advisor in Shanghai",
        "entry_kind": "demand",
        "target": "suppliers",
        "top_k": 5,
    },
)
```

## Model API Integration Examples

The default recommended approach is the built-in `OpenAIChatCompletionsModel`.
It supports OpenAI and OpenAI-compatible providers by switching `model`,
`base_url`, or `openai_client` without changing pipeline code.

```python
from openai import AsyncOpenAI
from neoxlink_sdk import OpenAIChatCompletionsModel, ProcurementIntentEngine

model = OpenAIChatCompletionsModel(
    model="<your-model-name>",
    openai_client=AsyncOpenAI(base_url="<your-provider-url>", api_key="<your-api-key-or-local-token>"),
)
# Users can set any model/provider URL freely; no provider-specific hardcoding required.
# UNSPSC candidates are inferred by the model from user input (with deterministic fallback checks).
```

Additional provider-specific examples are under `examples/model_apis/`:

- OpenAI official SDK (`01_openai_model_adapter.py`)
- Anthropic official SDK (`02_anthropic_model_adapter.py`)
- Google GenAI official SDK (`03_gemini_model_adapter.py`)
- Ollama Python SDK (`04_ollama_model_adapter.py`)
- Multi-provider router (`05_model_router_adapter.py`)

Each adapter is built against the same `ModelAdapter` contract and can be used
with `ProcurementIntentEngine`.

Install model provider SDKs for these examples:

```bash
pip install -e ".[model_examples]"
```

## Plugin Registry Example

```python
from neoxlink_sdk import OpenAIChatCompletionsModel, PluginRegistry, ProcurementIntentEngine

registry = PluginRegistry()
registry.register_model_adapter(
    "openai_compatible_default",
    lambda: OpenAIChatCompletionsModel(model="<your-model-name>", base_url="<your-provider-url>"),
)
registry.register_data_source("market_feed", lambda: MarketFeedConnector())
registry.register_ranking_strategy("cost_aware", lambda: cost_aware_strategy)

engine = ProcurementIntentEngine(
    data_source=registry.create_data_source("market_feed"),
    model_adapter=registry.create_model_adapter("openai_compatible_default"),
    ranking_strategy=registry.create_ranking_strategy("cost_aware"),
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
- `examples/06_plugin_registry.py` - plugin registration and runtime composition
- `examples/07_open_source_pipeline.py` - open-source reference module pipeline
- `examples/08_startup_policy_realworld.py` - real-world startup consulting advisor (interactive)
- `examples/model_apis/` - model provider integration examples

## Community and OSS Governance

- `community/README.md` - community playbook
- `community/FOUNDER_REVIEW.md` - founder-level project review
- `CONTRIBUTING.md` - contribution guide
- `CODE_OF_CONDUCT.md` - collaboration standard

## Data Quality Incentives

Submission view tracking, satisfaction scoring, referral-traffic incentives, and
provider reward logic are implemented in the private backend repository.

This public SDK only exposes collaborative/open foundational mechanisms and does
not include monetization or private growth logic.

## Real-World Interactive Use Case

The repository includes a practical interactive advisor flow for your exact scenario:

1. configure your own model (for example Qwen via OpenAI-compatible endpoint)
2. enter: "I'm looking for startup consulting services."
3. model asks follow-up clarification questions
4. model checks if current evidence is sufficient
5. if insufficient, it discovers public sources, fetches data, analyzes and summarizes
6. asks whether your needs are fully met; if not, it continues searching

Run:

```bash
pip install -e ".[model_examples]"
python examples/08_startup_policy_realworld.py
```

## QR Code

![NeoXlink QR Code](/Users/neo/Desktop/NEO-AI/qrcode.jpg)

## License

MIT
