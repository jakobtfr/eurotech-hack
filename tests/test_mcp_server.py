from __future__ import annotations

import json
import sys
from typing import Any, cast

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.common import REPO_ROOT


def test_mcp_server_stdio_smoke() -> None:
    anyio.run(_exercise_server)


async def _exercise_server() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp_server"],
        cwd=REPO_ROOT,
    )
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()

        tools = await session.list_tools()
        tool_names = {tool.name for tool in tools.tools}
        assert {
            "list_demo_examples",
            "get_tile_evidence",
            "trace_source",
            "summarize_claim_boundaries",
            "validate_demo_artifacts",
        } <= tool_names

        examples_result = await session.call_tool("list_demo_examples", {})
        examples_payload = cast(dict[str, Any], examples_result.structuredContent)
        examples = cast(list[dict[str, Any]], examples_payload["result"])
        assert len(examples) >= 4
        assert {example["verdict"] for example in examples} >= {"PASS", "REVIEW", "HOLD"}

        tile_id = cast(str, examples[0]["tile_id"])
        evidence_result = await session.call_tool("get_tile_evidence", {"tile_id": tile_id})
        evidence = cast(dict[str, Any], evidence_result.structuredContent)
        assert evidence["tile_id"] == tile_id
        assert evidence["claim_boundary"]

        validation_result = await session.call_tool("validate_demo_artifacts", {"check_files": True})
        validation = cast(dict[str, Any], validation_result.structuredContent)
        assert validation["manifest_exists"] is True
        assert validation["schema_ok"] is True
        assert isinstance(validation["missing_files"], list)

        resource = await session.read_resource("demo://manifest")
        manifest = json.loads(resource.contents[0].text)
        assert manifest["default_example_id"] == "miic_sem_w12__x0000_y0000_s0512"

        prompt = await session.get_prompt("audit_tile", {"tile_id": tile_id})
        assert tile_id in prompt.messages[0].content.text
