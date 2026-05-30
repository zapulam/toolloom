import pytest

from toolloom import ToolRegistry, tool

pytest.importorskip("fastmcp")


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


def test_fastmcp_adapter_returns_server() -> None:
    server = ToolRegistry([add]).to_fastmcp(name="Math Tools")

    assert server is not None
    assert server.__class__.__name__ == "FastMCP"
