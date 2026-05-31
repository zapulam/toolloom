import pytest

from toolloom import ToolRegistry, tool

pytest.importorskip("crewai.tools")


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


def test_crewai_adapter_exports_tool() -> None:
    tools = ToolRegistry([add]).to_crewai()

    assert len(tools) == 1
    assert tools[0].name == "add"
    assert tools[0]._run(a=2, b=3) == 5
