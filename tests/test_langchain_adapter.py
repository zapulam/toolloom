import pytest

from toolloom import ToolRegistry, tool

pytest.importorskip("langchain_core.tools")


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


def test_langchain_adapter_exports_structured_tool() -> None:
    langchain_tools = ToolRegistry([add]).to_langchain()

    assert len(langchain_tools) == 1
    assert langchain_tools[0].name == "add"
    assert langchain_tools[0].invoke({"a": 2, "b": 3}) == 5
