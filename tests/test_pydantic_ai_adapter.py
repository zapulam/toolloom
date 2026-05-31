import pytest

from toolloom import ToolRegistry, tool

pytest.importorskip("pydantic_ai")


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


def test_pydantic_ai_adapter_exports_tool() -> None:
    tools = ToolRegistry([add]).to_pydantic_ai()

    assert len(tools) == 1
    assert tools[0].name == "add"
