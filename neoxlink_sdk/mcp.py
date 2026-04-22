from __future__ import annotations

from typing import Any

from .engine import ProcurementIntentEngine
from .models import SkillRequest
from .skill import NeoxlinkSkill

_PARSE_PREVIEW_DESC = """UNSPSC Standardization & B2B intent parsing (preview only, no server-side confirmation).

Use when the agent needs a structured, taxonomy-aligned interpretation of messy natural language
**without** creating a confirmed commercial record yet. This is the MCP equivalent of a
**parse_intent** step for **Agent Commerce** workflows: you receive a draft `ParsedPreview` that may
include an 8-digit **UNSPSC** code plus human-readable segment name, extracted entities,
constraints, keywords, confidence, and quality flags.

**When to call:** early in the funnel—discovery, quoting, RFP triage, supplier shortlisting—when you
want **Standardization** signals before committing. **When not to call:** if the user or policy
already approved persistence; prefer `neoxlink.confirmed_submit` instead.

**Returns:** `SkillResponse` with `status="preview_ready"` and a `draft` containing
`confirmation_token` (needed if you later confirm via the HTTP API) and `preview` (UNSPSC
classification may be present depending on backend/heuristics).

**Keywords:** Standardization, UNSPSC, B2B, Agent Commerce, procurement taxonomy, structured preview."""

_CONFIRMED_SUBMIT_DESC = """UNSPSC Standardization with durable structured submit (parse + confirm in one MCP call).

Use when the agent should move from conversational understanding to an **executable B2B / Agent
Commerce** artifact: this runs the same pipeline as `neoxlink.parse_preview` but **auto-confirms**,
producing a confirmed entry id and (by default) triggering **resolve** so the host can obtain
answers or next-step handoff metadata.

**When to call:** the user explicitly wants to “submit”, “file this demand/supply”, “make it
official”, or your automation policy allows auto-confirm. **When not to call:** ambiguous
legal/procurement gates—use `neoxlink.parse_preview` first and obtain human approval.

**Arguments:** `overrides` lets agents or humans adjust structured fields (including UNSPSC hints)
before confirmation; `resolve_after_confirm` (default true) controls whether resolve runs
immediately after confirm.

**Keywords:** Standardization, UNSPSC, B2B, Agent Commerce, structured record, transaction bridge."""

_MATCH_INTENT_DESC = """Local **match_supply** / **match_demand** ranking over a configured in-memory procurement
engine (optional; requires `NEOXLINK_ENABLE_MATCH=1` on the server).

Runs a staged pipeline: intent parse → UNSPSC candidate inference → optional clarification state →
normalized intent → ranked suppliers or buyers. This complements cloud `neoxlink.confirmed_submit`
by giving agents a **deterministic, offline-friendly** matching surface for demos, tests, or
air-gapped Standardization workflows.

**When to call:** you need ranked counterparties **without** calling the remote NeoXlink API, and the
operator enabled the local engine. **When not to call:** production matching against live marketplace
data—use HTTP search/resolve flows instead.

**Arguments:** `target` selects `suppliers` vs `buyers`; `top_k` bounds results (1–50);
`clarification_answers` fills structured follow-up answers when the engine requests clarification.

**Keywords:** Standardization, UNSPSC, B2B, Agent Commerce, supply-demand matching."""


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
