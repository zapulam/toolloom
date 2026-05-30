import asyncio
from pathlib import Path

from toolloom import SkillRegistry, ToolRegistry, skill, tool

SKILL_PATH = Path(__file__).with_name("skills") / "math_strategy.md"


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


@skill(
    description="Read the math strategy instructions for the agent.",
    markdown_path=str(SKILL_PATH),
)
def math_strategy() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


tool_registry = ToolRegistry([add])
skill_registry = SkillRegistry([math_strategy])

# Add executable tools first, then add markdown-backed skills to the same MCP app.
mcp = tool_registry.to_fastmcp(name="Math Tools")
skill_registry.add_to_fastmcp(mcp)


async def list_mcp_tool_names() -> list[str]:
    """Return the tool names currently registered on the FastMCP app."""

    tools = await mcp.list_tools()
    return [tool.name for tool in tools]


if __name__ == "__main__":
    print(asyncio.run(list_mcp_tool_names()))
    mcp.run()
