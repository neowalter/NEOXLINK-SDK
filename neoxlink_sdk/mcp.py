from __future__ import annotations

from typing import Any

from .engine import ProcurementIntentEngine
from .models import SkillRequest
from .skill import NeoxlinkSkill

_PARSE_PREVIEW_DESC = """Convert natural language into a machine-readable **Structured Preview**
(no server-side confirmation).

Use when the agent must translate messy user text into a schema-aligned draft **before** a durable
record is created. Typical `ParsedPreview` content includes optional 8-digit **UNSPSC** code + name
(for goods/services), extracted entities, constraints, keywords, confidence, and quality flags—suitable
for CRM, ERP, marketplaces, procurement, or custom backends.

**When to call:** discovery, triage, quoting, or any step where you need **structured intent** first.
**When not to call:** the user or policy has already approved persistence; prefer
`neoxlink.confirmed_submit` instead.

**Returns:** `SkillResponse` with `status="preview_ready"` and a `draft` containing
`confirmation_token` (for later HTTP confirm) and `preview` (UNSPSC may be present per backend).

**Keywords:** natural language, structured intent, UNSPSC, system integration, MCP, Agent interoperability."""

_CONFIRMED_SUBMIT_DESC = """Durable structured submit (parse + auto-confirm in one MCP call).

Use when conversational input should become a **confirmed, machine-readable record** downstream: same
pipeline as `neoxlink.parse_preview` but **auto-confirmed**, with a stable entry id and (by default)
**resolve** for answers or handoff—whether the destination is supply chain, ERP, or another system.

**When to call:** the user says “submit”, “create the ticket/record”, “make it official”, or policy
allows auto-confirm. **When not to call:** high-risk or policy-ambiguous cases—use
`neoxlink.parse_preview` and human approval first.

**Arguments:** `overrides` adjust structured fields (including UNSPSC hints) before confirm;
`resolve_after_confirm` (default true) runs resolve after confirm.

**Keywords:** structured record, UNSPSC, enterprise integration, MCP, natural language to API payload."""

_MATCH_INTENT_DESC = """Local **match_supply** / **match_demand** ranking over a configured in-memory matching
engine (optional; `NEOXLINK_ENABLE_MATCH=1` on the server; reference implementation is procurement-oriented).

Runs: intent parse → UNSPSC inference → optional clarification → normalized intent → ranked
counterparties. Useful for **offline** demos, tests, or air-gapped environments; swap data sources in
custom deployments to cover other matching domains.

**When to call:** ranked matches are needed **without** the remote NeoXlink API and the local engine
is enabled. **When not to call:** production catalog search against live services—use HTTP flows.

**Arguments:** `target` = `suppliers` vs `buyers`; `top_k` 1–50; `clarification_answers` for follow-ups.

**Keywords:** local matching, UNSPSC, supply-demand, structured intent, MCP."""


class NeoxlinkMCPAdapter:
    """Exposes SDK flow as MCP-like tool methods."""

    def __init__(self, skill: NeoxlinkSkill, engine: ProcurementIntentEngine | None = None) -> None:
        self.skill = skill
        self.engine = engine

    def list_tools(self) -> list[dict[str, Any]]:
        tools = [
            {
                "name": "neoxlink.parse_preview",
                "description": _PARSE_PREVIEW_DESC,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": (
                                "Raw natural-language demand or supply description to normalize "
                                "(any language; English works best with packaged heuristics)."
                            ),
                            "minLength": 1,
                        },
                        "entry_kind": {
                            "type": "string",
                            "enum": ["demand", "supply"],
                            "description": "Commercial direction: buyer intent vs seller/offering intent.",
                            "default": "demand",
                        },
                        "metadata": {
                            "type": "object",
                            "description": (
                                "Opaque key-value bag forwarded to `/v1/entries/parse` "
                                "(routing, tenant, CRM ids)."
                            ),
                            "additionalProperties": True,
                        },
                        "use_own_model": {
                            "type": "boolean",
                            "description": (
                                "When true, hints billing metadata to use the caller's model "
                                "configuration where supported."
                            ),
                            "default": False,
                        },
                    },
                    "required": ["text"],
                },
            },
            {
                "name": "neoxlink.confirmed_submit",
                "description": _CONFIRMED_SUBMIT_DESC,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Raw NL to parse, confirm, and optionally resolve.",
                            "minLength": 1,
                        },
                        "entry_kind": {
                            "type": "string",
                            "enum": ["demand", "supply"],
                            "description": "Whether this entry represents purchasing demand or sell-side supply.",
                            "default": "demand",
                        },
                        "metadata": {
                            "type": "object",
                            "description": (
                                "Forwarded verbatim to parse; may include nested `billing` for model routing."
                            ),
                            "additionalProperties": True,
                        },
                        "overrides": {
                            "type": "object",
                            "description": (
                                "Field overrides applied at confirm time (e.g. `unspsc_code`, "
                                "`unspsc_name`, category fixes). The SDK pre-fills UNSPSC from the "
                                "preview when available."
                            ),
                            "additionalProperties": True,
                        },
                        "resolve_after_confirm": {
                            "type": "boolean",
                            "description": "If true (default), calls resolve immediately after confirmation.",
                            "default": True,
                        },
                        "use_own_model": {
                            "type": "boolean",
                            "description": "Billing hint for BYO-model execution on supported backends.",
                            "default": False,
                        },
                    },
                    "required": ["text"],
                },
            },
        ]
        if self.engine is not None:
            tools.append(
                {
                    "name": "neoxlink.match_intent",
                    "description": _MATCH_INTENT_DESC,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Procurement text to run through the local matching pipeline.",
                                "minLength": 1,
                            },
                            "entry_kind": {
                                "type": "string",
                                "enum": ["demand", "supply"],
                                "description": "Perspective for normalization and ranking.",
                                "default": "demand",
                            },
                            "target": {
                                "type": "string",
                                "enum": ["suppliers", "buyers"],
                                "description": (
                                    "Rank suppliers (sell-side partners) vs buyers "
                                    "(purchase-side partners)."
                                ),
                                "default": "suppliers",
                            },
                            "top_k": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 50,
                                "description": "Maximum ranked matches to return.",
                                "default": 5,
                            },
                            "clarification_answers": {
                                "type": "object",
                                "description": "Map of clarification question `key` → user/agent answer strings.",
                                "additionalProperties": {"type": "string"},
                            },
                        },
                        "required": ["text"],
                    },
                }
            )
        return tools

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        args = dict(arguments)
        if tool_name == "neoxlink.parse_preview":
            args["auto_confirm"] = False
            response = self.skill.run(SkillRequest.model_validate(args))
            return response.model_dump(mode="json")

        if tool_name == "neoxlink.confirmed_submit":
            args["auto_confirm"] = True
            response = self.skill.run(SkillRequest.model_validate(args))
            return response.model_dump(mode="json")

        if tool_name == "neoxlink.match_intent":
            if self.engine is None:
                raise ValueError("No ProcurementIntentEngine configured for neoxlink.match_intent")
            result = self.engine.run(
                text=str(args["text"]),
                entry_kind=str(args.get("entry_kind", "demand")),
                target=str(args.get("target", "suppliers")),
                top_k=int(args.get("top_k", 5)),
                clarification_answers=args.get("clarification_answers"),
            )
            return result.model_dump(mode="json")

        raise ValueError(f"Unknown tool: {tool_name}")
