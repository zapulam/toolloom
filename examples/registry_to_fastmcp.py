from toolloom import ToolRegistry, tool


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


registry = ToolRegistry([add])
mcp = registry.to_fastmcp(name="Math Tools")


if __name__ == "__main__":
    mcp.run()
