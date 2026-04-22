"""Stdio MCP server wrapping `NeoxlinkMCPAdapter` (requires optional `[mcp]` extra)."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from .client import NeoXlinkClient
from .engine import InMemoryDataSource, ProcurementIntentEngine
from .mcp import NeoxlinkMCPAdapter
from .pipeline import StructuredSubmissionPipeline
from .skill import NeoxlinkSkill


def _import_mcp() -> Any:
    try:
        from mcp.server import Server  # type: ignore[import-not-found]
        from mcp.server.stdio import stdio_server  # type: ignore[import-not-found]

        from mcp import types  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - env hint for operators
        raise RuntimeError(
            "The MCP server requires the `mcp` package. Install with: pip install 'neoxlink-sdk[mcp]'"
        ) from exc
    return types, Server, stdio_server


def build_adapter() -> NeoxlinkMCPAdapter:
    base_url = os.environ.get("NEOXLINK_BASE_URL", "https://neoxailink.com")
    api_key = os.environ.get("NEOXLINK_API_KEY")
    client = NeoXlinkClient(base_url=base_url, api_key=api_key)
    skill = NeoxlinkSkill(StructuredSubmissionPipeline(client))
    engine: ProcurementIntentEngine | None = None
    if os.environ.get("NEOXLINK_ENABLE_MATCH", "").lower() in ("1", "true", "yes"):
        engine = ProcurementIntentEngine(data_source=InMemoryDataSource([]))
    return NeoxlinkMCPAdapter(skill, engine=engine)


def _run_stdio(adapter: NeoxlinkMCPAdapter) -> None:
    types, Server, stdio_server = _import_mcp()
    anyio: Any
    import importlib

    anyio = importlib.import_module("anyio")

    async def handle_list_tools(
        _ctx: Any, _params: Any
    ) -> Any:
        tools_out = []
        for spec in adapter.list_tools():
            tools_out.append(
                types.Tool(
                    name=spec["name"],
                    description=spec.get("description", ""),
                    input_schema=spec.get("input_schema", {}),
                )
            )
        return types.ListToolsResult(tools=tools_out)

    async def handle_call_tool(_ctx: Any, params: Any) -> Any:
        name = params.name
        args = params.arguments or {}
        payload = adapter.call_tool(name, dict(args))
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])

    app = Server(
        "neoxlink-sdk",
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )

    async def arun() -> None:
        async with stdio_server() as streams:
            await app.run(
                streams[0],
                streams[1],
                app.create_initialization_options(),
            )

    anyio.run(arun)


def main() -> None:
    if os.environ.get("NEOXLINK_MCP_REPL_HELP"):
        _print_help()
        return
    adapter = build_adapter()
    _run_stdio(adapter)


def _print_help() -> None:
    print(
        "neoxlink-mcp: stdio MCP server. Set NEOXLINK_API_KEY. "
        "Optional: NEOXLINK_BASE_URL, NEOXLINK_ENABLE_MATCH=1 for neoxlink.match_intent.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
