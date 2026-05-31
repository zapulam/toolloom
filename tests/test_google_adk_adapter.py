import pytest

from toolloom import ToolRegistry, tool

pytest.importorskip("google.adk.tools")


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


def test_google_adk_adapter_exports_function_tool() -> None:
    tools = ToolRegistry([add]).to_google_adk()

    assert len(tools) == 1
    assert tools[0].name == "add"
