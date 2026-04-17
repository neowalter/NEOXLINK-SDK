from __future__ import annotations

from typing import Any

from .engine import ProcurementIntentEngine
from .models import SkillRequest
from .skill import NeoxlinkSkill


class NeoxlinkMCPAdapter:
    """Exposes SDK flow as MCP-like tool methods."""

    def __init__(self, skill: NeoxlinkSkill, engine: ProcurementIntentEngine | None = None) -> None:
        self.skill = skill
        self.engine = engine

    def list_tools(self) -> list[dict[str, Any]]:
        tools = [
            {
                "name": "neoxlink.parse_preview",
                "description": "Parse natural language into structured preview with UNSPSC code/name, without confirmation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "entry_kind": {"type": "string", "enum": ["demand", "supply"]},
                        "metadata": {"type": "object"},
                        "use_own_model": {"type": "boolean"},
                    },
                    "required": ["text"],
                },
            },
            {
                "name": "neoxlink.confirmed_submit",
                "description": "Parse then confirm into structured record with UNSPSC standardization in one MCP call.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "entry_kind": {"type": "string", "enum": ["demand", "supply"]},
                        "metadata": {"type": "object"},
                        "overrides": {"type": "object"},
                        "resolve_after_confirm": {"type": "boolean"},
                        "use_own_model": {"type": "boolean"},
                    },
                    "required": ["text"],
                },
            },
        ]
        if self.engine is not None:
            tools.append(
                {
                    "name": "neoxlink.match_intent",
                    "description": "Run staged procurement intent pipeline and return ranked suppliers/buyers.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "entry_kind": {"type": "string", "enum": ["demand", "supply"]},
                            "target": {"type": "string", "enum": ["suppliers", "buyers"]},
                            "top_k": {"type": "integer", "minimum": 1, "maximum": 50},
                            "clarification_answers": {"type": "object"},
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
