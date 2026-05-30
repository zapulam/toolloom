from toolloom import ToolRegistry, tool


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


registry = ToolRegistry([add])
langgraph_tools = registry.to_langgraph()


if __name__ == "__main__":
    print(langgraph_tools)
