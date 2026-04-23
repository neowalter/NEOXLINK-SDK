"""Stdio MCP server wrapping `NeoxlinkMCPAdapter` (requires optional `[mcp]` extra).

**Compatibility:** Pin the `mcp` package to the range declared in `pyproject.toml` under
`[project.optional-dependencies] mcp`. The Python SDK uses the stdio transport with
decorator-registered handlers (`list_tools`, `call_tool`, `list_resources`, `read_resource`).
When upstream introduces breaking changes, update `_import_mcp`, handlers, and
`tests/test_mcp_*.py` in the same PR. See `docs/wiki/mcp-integration.md` for a host-facing
summary.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
from typing import Any

from pydantic import AnyUrl

from .catalog import CATALOG, default_unspsc_catalog_path
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
            "The MCP server requires the `mcp` package. Install with: pip install 'neoxlink[mcp]'"
        ) from exc
    return types, Server, stdio_server


def _pkg_version() -> str:
    try:
        from importlib.metadata import version

        return version("neoxlink")
    except Exception:  # pragma: no cover
        return "0.6.3"


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
    anyio = importlib.import_module("anyio")

    instructions = (
        "NEOXLINK: UNSPSC Standardization, B2B taxonomy mapping, and Agent Commerce tooling. "
        "Prefer `neoxlink.parse_preview` for reversible previews; use `neoxlink.confirmed_submit` when the user "
        "or policy authorizes a durable structured record. Read `unspsc://catalog` or "
        "`unspsc://entry/{code}` resources for the packaged UNSPSC subset shipped with the SDK."
    )
    app = Server(
        "neoxlink",
        version=_pkg_version(),
        instructions=instructions,
    )

    @app.list_tools()
    async def handle_list_tools(_req: Any) -> Any:
        tools: list[Any] = []
        for spec in adapter.list_tools():
            tools.append(
                types.Tool(
                    name=spec["name"],
                    description=spec.get("description", ""),
                    inputSchema=spec.get("input_schema", {}),
                )
            )
        return types.ListToolsResult(tools=tools)

    @app.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
        return adapter.call_tool(name, dict(arguments or {}))

    @app.list_resources()
    async def handle_list_resources(_req: Any) -> list[Any]:
        return [
            types.Resource(
                name="unspsc-packaged-catalog",
                title="Packaged UNSPSC subset (JSON)",
                uri=AnyUrl("unspsc://catalog"),
                description=(
                    "Full UNSPSC keyword catalog bundled with neoxlink for Standardization, "
                    "offline Agent Commerce demos, and deterministic taxonomy lookups (B2B)."
                ),
                mimeType="application/json",
            )
        ]

    @app.list_resource_templates()
    async def handle_list_resource_templates() -> list[Any]:
        return [
            types.ResourceTemplate(
                name="unspsc-entry-by-code",
                title="UNSPSC entry by 8-digit code",
                uriTemplate="unspsc://entry/{code}",
                description=(
                    "Returns one JSON object {code, name, keywords} from the packaged UNSPSC subset when "
                    "`code` matches; supports Agent Commerce and Standardization workflows."
                ),
                mimeType="application/json",
            )
        ]

    @app.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        u = str(uri)
        if u == "unspsc://catalog":
            return default_unspsc_catalog_path().read_text(encoding="utf-8")
        prefix = "unspsc://entry/"
        if u.startswith(prefix):
            code = u.removeprefix(prefix)
            for entry in CATALOG:
                if entry.code == code:
                    payload = {"code": entry.code, "name": entry.name, "keywords": list(entry.keywords)}
                    return json.dumps(payload, ensure_ascii=False, indent=2)
            raise ValueError(f"Unknown UNSPSC code in packaged catalog: {code}")
        raise ValueError(f"Unsupported resource URI: {u}")

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
        "Optional: NEOXLINK_BASE_URL, NEOXLINK_ENABLE_MATCH=1 for neoxlink.match_intent. "
        "Resources: unspsc://catalog, unspsc://entry/{code}.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
