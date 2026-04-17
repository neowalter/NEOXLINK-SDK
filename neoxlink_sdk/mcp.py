from __future__ import annotations

from typing import Any

from .models import SkillRequest
from .skill import NeoxlinkSkill


class NeoxlinkMCPAdapter:
    """Exposes SDK flow as MCP-like tool methods."""

    def __init__(self, skill: NeoxlinkSkill) -> None:
        self.skill = skill

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "neoxlink.parse_preview",
                "description": "Parse natural language into structured preview with UNSPSC code/name, without confirmation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "entry_kind": {"type": "string", "enum": ["demand", "supply"]},
                        "metadata": {"type": "object"},
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
                    },
                    "required": ["text"],
                },
            },
        ]

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

        raise ValueError(f"Unknown tool: {tool_name}")
