from toolloom import ToolRegistry, tool


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


registry = ToolRegistry([add])
langchain_tools = registry.to_langchain()


if __name__ == "__main__":
    print(langchain_tools[0].invoke({"a": 1, "b": 2}))
