import pytest

from toolloom import SkillRegistry, ToolRegistry, skill, tool


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


@skill(description="Read the math strategy instructions.")
def math_strategy() -> str:
    return "# Math Strategy"


def test_openai_agents_adapter_exports_skill_tool() -> None:
    pytest.importorskip("agents")

    tools = SkillRegistry([math_strategy]).to_openai_agents()

    assert len(tools) == 1
    assert tools[0].name == "math_strategy"


def test_langchain_adapter_exports_skill_structured_tool() -> None:
    pytest.importorskip("langchain_core.tools")

    tools = SkillRegistry([math_strategy]).to_langchain()

    assert len(tools) == 1
    assert tools[0].name == "math_strategy"
    assert tools[0].invoke({}) == "# Math Strategy"


@pytest.mark.asyncio
async def test_fastmcp_adapter_adds_skills_to_existing_server() -> None:
    pytest.importorskip("fastmcp")

    server = ToolRegistry([add]).to_fastmcp(name="Math Tools")
    SkillRegistry([math_strategy]).add_to_fastmcp(server)

    tool_names = [tool.name for tool in await server.list_tools()]
    assert tool_names == ["add", "math_strategy"]


def test_langgraph_adapter_returns_skill_tools() -> None:
    pytest.importorskip("langchain_core.tools")

    tools = SkillRegistry([math_strategy]).to_langgraph()

    assert len(tools) == 1
    assert tools[0].name == "math_strategy"
