import pytest

from toolloom import ToolRegistry, tool

pytest.importorskip("agents")


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


def test_openai_agents_adapter_exports_function_tool() -> None:
    tools = ToolRegistry([add]).to_openai_agents()

    assert len(tools) == 1
    assert tools[0].name == "add"
