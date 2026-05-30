import pytest

from toolloom import ToolRegistry, tool

pytest.importorskip("langchain_core.tools")


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


def test_langgraph_adapter_returns_langchain_tools() -> None:
    tools = ToolRegistry([add]).to_langgraph()

    assert len(tools) == 1
    assert tools[0].name == "add"


def test_langgraph_tool_node_when_installed() -> None:
    pytest.importorskip("langgraph.prebuilt")

    node = ToolRegistry([add]).to_langgraph_tool_node()

    assert node is not None
