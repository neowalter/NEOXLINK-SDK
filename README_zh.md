# NEOXLINK-SDK

[![PyPI version](https://img.shields.io/pypi/v/neoxlink.svg)](https://pypi.org/project/neoxlink/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6f42c1.svg)](https://modelcontextprotocol.io/)
[![UNSPSC 手册](https://img.shields.io/badge/docs-UNSPSC%20快速查阅-blue.svg)](docs/wiki/unspsc-quick-ref.md)
[![MCP 集成](https://img.shields.io/badge/docs-MCP%20集成-6f42c1.svg)](docs/wiki/mcp-integration.md)
[![Agent 全渠道](https://img.shields.io/badge/docs-Agent%20全渠道-2ea043.svg)](docs/wiki/agent-channel-matrix.md)

**自然语言需求 → 机器可读的结构化表示** —— 将口语化描述变成 **系统能解析、路由与执行的强类型意图与记录**，不局限于单一业务场景；可对接 **采购、销售、运营、客服、合规** 等既有系统。

> **愿景：** NEOXLINK-SDK 解决「模型听懂了一句话」与「业务系统能消费确定性载荷」之间的断层。以 **UNSPSC 全球标准（Code + Name）** 为商品/服务归一化主轴，通过 **Structured Preview**、人工或 Agent 确认、**结构化落库** 与 **AI Resolve**，让同一套管线可接入 **CRM、ERP、B2B 平台、内部工具或自研 API**；**插件、覆盖与策略门** 支持多租户与个性化。原生支持 **Skill 运行时** 与 **MCP（Model Context Protocol）** 工具暴露，便于 agents 与现有软件栈集成。

English: [`README.md`](README.md) — 同仓中文手册与 MCP 说明见上列 Badge。

- **分层架构（HTTP / 本地 UNSPSC / 编排，与 CI 一致）：** [`docs/wiki/repository-layout.md`](docs/wiki/repository-layout.md)；概览图亦见 [`README.md` — System architecture](README.md#system-architecture-natural-language--structured-system-ready-output)

## 痛点与解法

对话式 AI 擅长复述，但 **CRM、ERP、采购、市场、内部自动化** 等系统需要 **编码、约束与可校验字段**，而非大段自然语言。NEOXLINK-SDK 将需求映射为 **可机读的结构化意图**（在适用场景对齐 **UNSPSC**），输出 **Structured Preview** 与强类型载荷，并可在同一归一化轴上支持 **Supply-Demand Matching（示例域：供需匹配）** 等下游流程。

| 维度 | 传统 AI 对话 | NEOXLINK-SDK |
| --- | --- | --- |
| 输出形态 | 自由文本 | **Structured Preview** + 强类型载荷 |
| 分类体系 | 临时标签 | **UNSPSC（Code + Name）** 等归一化（商品/服务场景） |
| 落地能力 | 弱 | 解析 → 确认 → 结构化落库 → **Resolve / 匹配** |
| Agent 集成 | 依赖提示词拼凑 | **Skill** 适配层 + **MCP** 工具面 |
| 匹配能力 | 语义「感觉」 | 基于归一意图的 **Supply-Demand Matching** 与可解释信号（可扩展至其他域） |

## 核心特性

- **自然语言 → 结构化意图** — 需求可变为下游系统能消费的字段与记录。  
- **UNSPSC 优先（商品/服务）** — 需求与供给两侧可统一 **Code + Name**。  
- **Structured Preview** — 在落库前由 LLM 生成可确认的结构化预览。  
- **人机 / Agent 确认** — 覆盖字段与策略门闸，支持个性化与合规。  
- **结构化持久化** — 确认后的记录进入可对接 **现有系统** 的流水线。  
- **AI Resolve** — 直答或将请求导向正确的后端/履约链。  
- **Supply-Demand Matching** — 分阶段 `ProcurementIntentEngine`，数据与排序可插拔（内置参考实现，可拓展到其他业务）。  
- **Agent Interoperability** — `NeoxlinkSkill`、`NeoxlinkMCPAdapter`、链式编排一等公民。  
- **MCP 工具暴露** — 稳定工具名如 `neoxlink.parse_preview`、`neoxlink.confirmed_submit`。

## 核心流转

1. **自然语言输入** — 用户或 Agent 用口语描述需求。  
2. **LLM Structured Preview** — 意图被压缩为可机读预览（在适用场景包含 **UNSPSC**）。  
3. **用户 / Agent 确认** — 确认或修订；业务真值明确。  
4. **结构化落库** — 确认记录可对接 **你们的 API、ERP、SaaS 或自建服务**。  
5. **AI Resolve** — 回答、升级或连接对应下游流程。

## 快速开始

**安装**

```bash
pip install neoxlink
# 或从本仓库：
pip install -e .
```

**最简 Python：`SDK` + Structured Preview**

```python
from neoxlink import SDK

sdk = SDK(
    base_url="https://neoxailink.com",
    api_key="ak_live_xxx",  # 你的 NeoXlink API Key
)
draft = sdk.parse_preview(
    "我们需要欧盟零售上架前的包装合规咨询，时间紧。",
    entry_kind="demand",
)
print(draft.preview.unspsc.code, draft.preview.unspsc.name)
```

> 进阶用法可直接使用 `neoxlink_sdk`（`NeoXlinkClient`、`StructuredSubmissionPipeline`、`ProcurementIntentEngine`、`NeoxlinkMCPAdapter` 等）。详见 `examples/` 与下文架构表。

**运行示例**

```bash
pip install -e .
python examples/04_procurement_intent_engine.py
```

**MCP（Model Context Protocol）stdio 服务**

```bash
pip install 'neoxlink[mcp]'
export NEOXLINK_API_KEY=你的密钥
neoxlink-mcp
```

在 Claude Desktop、Cursor 等宿主中把 MCP 服务指向 `neoxlink-mcp` 命令，或参考配置模板 [`mcp/config.neoxlink.example.json`](mcp/config.neoxlink.example.json)。可选：设置 `NEOXLINK_ENABLE_MATCH=1` 以暴露 `neoxlink.match_intent`（本地匹配管线；自托管时接入自有数据源）。

## Agent 快速接入（MCP & Skill）

**三行指令：安装并启动 MCP（推荐 uvx，无虚拟环境）**

```bash
export NEOXLINK_API_KEY="你的密钥"
uvx --from 'neoxlink[mcp]' neoxlink-mcp
# 在 Cursor / Claude Code / Claude Desktop 中将上述进程注册为 MCP（stdio），随后在宿主内「列出工具」应看到 neoxlink.parse_preview、neoxlink.confirmed_submit。
```

若已习惯 pip：`pip install 'neoxlink[mcp]' && neoxlink-mcp`。宿主侧配置可复制根目录 [`mcp-config.json`](mcp-config.json) 或 [`mcp/config.neoxlink.example.json`](mcp/config.neoxlink.example.json)。需调试 MCP 时可使用 `npx -y @modelcontextprotocol/inspector`（常用于 HTTP 形态）；**本包默认 stdio**，以宿主 MCP 配置为准。

**全渠道一览（协议级发现优先，避免手工 Webhook）**

| 渠道 | 加载方式 |
| --- | --- |
| **本地 MCP** | `neoxlink-mcp`（`pip` / `uvx` 均可） |
| **MCP Registry（预览）** | `server.json` + `mcp-publisher`；详见 [mcp-integration.md](docs/wiki/mcp-integration.md) |
| **OpenClaw / ClawHub** | `SKILL.md`（AgentSkills）+ `openclaw skills install` / `clawhub`；示例见 [`integrations/openclaw-clawhub-skill/`](integrations/openclaw-clawhub-skill/) |
| **Hermes** | 在 Hermes 配置 MCP 服务以走 `discover_mcp_tools()`；原生扩展用独立插件包的 `hermes_agent.plugins` 入口 |
| **Skillshub 类目录** | 提交清单 [`integrations/skillshub/skill-manifest.json`](integrations/skillshub/skill-manifest.json)；运行态仍启动 `neoxlink-mcp` |

**结构化矩阵、核心清单与模板：** [docs/wiki/agent-channel-matrix.md](docs/wiki/agent-channel-matrix.md)。

## 应用场景

- **需要结构化前端的任意业务系统** — 会话、语音或邮件进线，落为 **CRM / ERP / 工单 / 内部 API** 能用的字段。  
- **全球采购与寻源（典型强场景）** — 以 **UNSPSC** 统一多地区请购与目录。  
- **跨境与合规** — 多语种需求映射到可比对、可审计的编码与记录。  
- **B2B 平台与多系统集成** — 可重复、可机读的 handoff。  
- **Agent 与自动化产品** — 通过 **MCP** 或 **Skill** 把「听懂」变成「能执行」，少造轮子。  
- **个性化与多租户** — 确认门、策略与插件区分客户与策略。  
- **Supply-Demand Matching** — 在归一意图上做可解释排序（仓库内参考引擎，可换数据源与行业）。

## 架构要点（v0.6.4）

| 模块 | 职责 |
| --- | --- |
| `neoxlink_sdk.client.NeoXlinkClient` | HTTP 层：`parse_entry`、`confirm_entry`、`resolve_entry`、`structured_submit`。 |
| `neoxlink_sdk.pipeline.StructuredSubmissionPipeline` | 编排解析 → 确认 → Resolve（`ParseDraft`、`ConfirmedEntry`、`ResolveResult`）。 |
| `neoxlink_sdk.engine.ProcurementIntentEngine` | 分阶段匹配：意图 → **UNSPSC** → 澄清 → 检索 → 排序。 |
| `neoxlink_sdk.skill.NeoxlinkSkill` | Skill 运行时适配（仅预览 / 自动确认）。 |
| `neoxlink_sdk.mcp.NeoxlinkMCPAdapter` | **MCP** 工具门面，强化 **Agent Interoperability**。 |
| `neoxlink_sdk.credits` | 计量计费与 BYOM 策略。 |
| `neoxlink_sdk.plugins.PluginRegistry` | 注册模型适配器、数据源、排序策略。 |

**开源社区结构**

1. [Templates](community/01_templates.md)  
2. [Examples](community/02_examples.md)  
3. [Plugins](community/03_plugins.md)  
4. [Contributors](community/04_contributors.md)  
5. [Ecosystem](community/05_ecosystem.md)  
6. [Adoption](community/06_adoption.md)

**治理与边界**

- [OPEN_SOURCE_SCOPE.md](OPEN_SOURCE_SCOPE.md)  
- [REPOSITORY_ARCHITECTURE.md](REPOSITORY_ARCHITECTURE.md)  
- [CONTRIBUTOR_WORKFLOW.md](CONTRIBUTOR_WORKFLOW.md)  
- [DATA_COLLABORATION_GUIDELINES.md](DATA_COLLABORATION_GUIDELINES.md)  
- [PROMPT_COLLABORATION.md](PROMPT_COLLABORATION.md)  
- [GOVERNANCE.md](GOVERNANCE.md)

## 更多示例

- `examples/01_structured_pipeline.py` — 解析 / 确认 / Resolve  
- `examples/02_skill_runtime.py` — Skill 运行时  
- `examples/03_chain_style.py` — 链式调用  
- `examples/04_procurement_intent_engine.py` — **UNSPSC** 匹配引擎  
- `examples/05_credits_and_byom.py` — 额度与 BYOM  
- `examples/06_plugin_registry.py` — 插件注册  
- `examples/07_open_source_pipeline.py` — 开源参考流水线  
- `examples/08_startup_policy_realworld.py` — 交互式顾问  
- `examples/model_apis/` — OpenAI、Anthropic、Gemini、Ollama、路由  
- `neoxlink-mcp` + `mcp/config.neoxlink.example.json` — 面向 Agent 宿主的 MCP stdio 服务  

模型示例可选依赖：

```bash
pip install -e ".[model_examples]"
```

## 社区

- [community/README.md](community/README.md)  
- [CONTRIBUTING.md](CONTRIBUTING.md)  
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## 许可证

MIT
