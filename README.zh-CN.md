# neoxlink-sdk

`neoxailink.com` 供需工作流的公开 Python SDK。

该 SDK 现已支持完整的结构化流程：

1. 用户提交自然语言文本
2. 后端 LLM 解析并优化为结构化预览
3. 用户（或 Agent）确认/编辑覆盖字段
4. 记录被确认为结构化数据
5. 可选的 resolve 步骤（AI 直答或回退引导）

SDK 使用 UNSPSC 作为需求（demand）与供给（supply）两侧的标准化规范，
采用标准 `code + name` 配对。

适用场景：

- 直接集成到应用/后端
- Skill 风格运行时
- MCP 风格工具暴露
- 结构化采购意图到供需匹配

## 开源社区结构

仓库按以下顺序组织，便于社区贡献：

1. [Templates](community/01_templates.md)
2. [Examples](community/02_examples.md)
3. [Plugins](community/03_plugins.md)
4. [Contributors](community/04_contributors.md)
5. [Ecosystem](community/05_ecosystem.md)
6. [Adoption](community/06_adoption.md)

## 开源范围与边界

- 开源范围定义：[`OPEN_SOURCE_SCOPE.md`](OPEN_SOURCE_SCOPE.md)
- 仓库模块架构：[`REPOSITORY_ARCHITECTURE.md`](REPOSITORY_ARCHITECTURE.md)
- 贡献流程：[`CONTRIBUTOR_WORKFLOW.md`](CONTRIBUTOR_WORKFLOW.md)
- 数据协作规范：[`DATA_COLLABORATION_GUIDELINES.md`](DATA_COLLABORATION_GUIDELINES.md)
- Prompt 协作框架：[`PROMPT_COLLABORATION.md`](PROMPT_COLLABORATION.md)
- 治理模型：[`GOVERNANCE.md`](GOVERNANCE.md)

## 安装

```bash
pip install -e .
```

最简 OpenAI 兼容接入方式：

```python
from neoxlink_sdk import MatchCandidate, create_engine

engine = create_engine(
    records=[
        MatchCandidate(
            partner_id="sup-001",
            partner_type="supplier",
            title="示例供应商",
            description="政策咨询支持",
            unspsc_codes=["80101500"],
        )
    ],
    model="<你的模型名>",
    base_url="<你的OpenAI兼容URL>",
    api_key="<你的密钥或本地token>",
)
```

## 设计原则

- **自然语言优先**：所有核心入口都支持自由文本输入。
- **默认结构化**：解析输出为强类型，并包含 UNSPSC 标准化结果。
- **可组合运行时**：支持直接 API Client、Pipeline 编排、Skill Adapter 与 MCP Adapter。
- **面向生产运维体验**：模型精简、阶段清晰、返回结构可预测。

## 架构（v0.4）

## 结构化匹配引擎（v0.3）

SDK 提供了可控的分阶段 `ProcurementIntentEngine` 供需匹配引擎：

1. 从碎片化自然语言中解析意图
2. 输出带置信度的 UNSPSC 候选映射
3. 触发澄清循环并生成精准问题
4. 归一化为下游可消费的标准查询对象
5. 从可插拔数据源进行混合检索
6. 基于解释信号执行确定性排序

该设计通过 `ModelAdapter` 保持模型/供应商无关，并通过 `DataSource` 支持可插拔连接器。

### `neoxlink_sdk.client.NeoXlinkClient`

`neoxailink.com` API 的 HTTP 客户端层，包含：

- `parse_entry()`
- `confirm_entry()`
- `resolve_entry()`
- `structured_submit()`（parse + confirm）
- 以及兼容旧版方法：`submit_entry()`、`get_entry()`、`search()`

### `neoxlink_sdk.pipeline.StructuredSubmissionPipeline`

parse -> confirm -> resolve 的编排层，带显式状态对象：

- `ParseDraft`
- `ConfirmedEntry`
- `ResolveResult`
- `PipelineOutcome`
- 内建 UNSPSC 分类增强（`code` + `name`）

### `neoxlink_sdk.chains.NeoxlinkSubmissionChain`

面向编排场景的 LangChain 风格调用接口（`invoke`）。

### `neoxlink_sdk.skill.NeoxlinkSkill`

围绕 pipeline 的 Skill 适配层：

- 仅返回预览，供人工确认
- 或自动确认并返回完整结果

### `neoxlink_sdk.mcp.NeoxlinkMCPAdapter`

面向 MCP 的工具门面，提供两个工具方法：

- `neoxlink.parse_preview`
- `neoxlink.confirmed_submit`

### `neoxlink_sdk.credits`（积分 + BYOM 控制）

用于产品计费规则的积分层：

- 每次搜索和匹配都会消耗积分
- 免费层每天可 `0` 成本提交 `5` 次 LLM 提取请求
- BYOM 模式（`use_own_model=True`）跳过平台提取计费
- `MeteredNeoXlinkClient` 将计费约束集成进标准 SDK 调用

### `neoxlink_sdk.plugins.PluginRegistry`

用于开源扩展点的插件注册中心：

- 注册模型适配器
- 注册数据连接器
- 注册排序策略
- 运行时按名称创建插件

---

## 快速开始：结构化工作流

```python
from neoxlink_sdk import NeoXlinkClient, StructuredSubmissionPipeline

client = NeoXlinkClient(
    base_url="https://neoxailink.com",
    api_key="ak_live_xxx",
)
pipeline = StructuredSubmissionPipeline(client)

# 1) parse/preview（LLM 优化后的结构化结果）
draft = pipeline.parse(
    text="I need a startup advisor for policy support in Shanghai.",
    entry_kind="demand",
    metadata={"channel": "sdk"},
)
print(draft.preview.unspsc.code, draft.preview.unspsc.name)

# 2) 用户确认（可选覆盖）
confirmed = pipeline.confirm(
    draft=draft,
    overrides={"constraints": {"region": ["Shanghai"]}},
)

# 3) 可选 resolve
resolved = pipeline.resolve(confirmed.raw_entry_id)
print(resolved.path, resolved.reason)
```

## 积分、免费额度与 BYOM

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

# 免费用户：每天前 5 次提取提交免费
pipeline.parse("Need startup advisor in Shanghai", entry_kind="demand")

# BYOM：接入你自己的模型/API 栈，跳过提取计费
pipeline.parse(
    "Need startup advisor; route extraction via my own model endpoint",
    entry_kind="demand",
    use_own_model=True,
)

# 搜索 + 匹配会消耗积分
client.search(query="startup advisor in Shanghai", entry_kind="supply")
```

## 快速开始：采购意图引擎

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

## Chain 风格用法（类似 LangChain）

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

## Skill 集成（Claude Code 风格）

该 SDK 提供了适配 Claude Code 工具运行时的稳定 Skill 合约：

- 输入对象：`SkillRequest`
- 输出对象：`SkillResponse`
- 可预测状态值：`preview_ready`、`confirmed`、`skipped`
- 显式人工确认开关：`auto_confirm=False`

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

# Claude Code 友好模式：首轮先返回预览，进入确认循环
preview = skill.run(
    SkillRequest(
        text="Offer enterprise packaging optimization consulting.",
        entry_kind="supply",
        auto_confirm=False,
    )
)
print(preview.status)  # preview_ready

# 二次调用确认并可选执行 resolve
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

## MCP 集成（Claude Code + OpenClaw）

### 使用 OpenClaw 快速安装

```bash
pip install neoxlink-sdk
# 如果尚未安装 OpenClaw：
pip install openclaw
```

### Claude Code 标准 MCP 工具面

`NeoxlinkMCPAdapter` 提供稳定、显式的工具名：

- `neoxlink.parse_preview`
- `neoxlink.confirmed_submit`
- `neoxlink.match_intent`（当配置 `ProcurementIntentEngine` 时可用）

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

## 模型 API 集成示例

默认推荐使用内置 `OpenAIChatCompletionsModel`。  
它可通过切换 `model`、`base_url` 或 `openai_client` 统一接入 OpenAI 及 OpenAI 兼容供应商。

```python
from openai import AsyncOpenAI
from neoxlink_sdk import OpenAIChatCompletionsModel

model = OpenAIChatCompletionsModel(
    model="<你的模型名>",
    openai_client=AsyncOpenAI(base_url="<你的供应商URL>", api_key="<你的密钥或本地token>"),
)
# 用户可自由输入模型名和供应商 URL，无需写死。
# UNSPSC 候选由模型基于用户输入推断（并保留确定性回退校验）。
```

`examples/model_apis/` 也提供多供应商模型接入示例：

- OpenAI（`01_openai_model_adapter.py`）
- Anthropic（`02_anthropic_model_adapter.py`）
- Gemini（`03_gemini_model_adapter.py`）
- Ollama 本地模型（`04_ollama_model_adapter.py`）
- 多模型路由（`05_model_router_adapter.py`）

安装扩展模型示例依赖：

```bash
pip install -e ".[model_examples]"
```

## UNSPSC 标准化

SDK 会将需求和供给文本都分类到 UNSPSC：

- 在 parse 阶段（`draft.preview.unspsc`）
- 并在 confirm overrides 中透传 `unspsc_code` / `unspsc_name`

如需单独分类：

```python
from neoxlink_sdk import classify_unspsc

code, name, confidence = classify_unspsc("Need startup policy consulting support")
print(code, name, confidence)
```

如果需要用于消歧的候选列表检索：

```python
from neoxlink_sdk import unspsc_candidates

for entry, score in unspsc_candidates("Need growth marketing campaign support", top_k=3):
    print(entry.code, entry.name, score)
```

## 核心工具

`core/` 目录仍可用于共享的匹配/去重基础能力：

- `core/schema.py`
- `core/dedup.py`
- `core/matching.py`

## 示例

- `examples/01_structured_pipeline.py` - parse/confirm/resolve 流程
- `examples/02_skill_runtime.py` - skill 运行时集成
- `examples/03_chain_style.py` - chain 风格调用
- `examples/04_procurement_intent_engine.py` - 分阶段 UNSPSC 匹配引擎
- `examples/05_credits_and_byom.py` - 积分计费与免费层额度
- `examples/06_plugin_registry.py` - 插件注册与运行时装配
- `examples/07_open_source_pipeline.py` - 开源模块化参考流水线
- `examples/08_startup_policy_realworld.py` - 真实可用的创业政策顾问（交互式）
- `examples/model_apis/` - 模型 API 集成示例

## 社区与治理

- `community/README.md` - 社区手册
- `community/FOUNDER_REVIEW.md` - 创始人视角项目评估
- `CONTRIBUTING.md` - 贡献指南
- `CODE_OF_CONDUCT.md` - 协作行为准则

## 数据质量激励机制

方案数据浏览量、满意度评分、引流激励和奖励策略由私有后端仓库实现。

公开 SDK 仅保留可协作的基础机制，不包含变现和私有增长逻辑。

## 真实场景交互用例

仓库已包含与你描述一致的可运行流程：

1. 配置你自己的模型（例如通过 OpenAI 兼容端点接入 Qwen）
2. 输入：“I’m looking for startup consulting services.”
3. 模型先进行多轮澄清
4. 判断现有证据是否充足
5. 若不足，则搜索公开来源、抓取信息并分析汇总
6. 询问你是否满足需求，若未满足则继续检索

运行方式：

```bash
pip install -e ".[model_examples]"
python examples/08_startup_policy_realworld.py
```

## 二维码

![NeoXlink 二维码](assets/qrcode.jpg)

## 许可证

MIT
