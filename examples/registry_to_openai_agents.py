from toolloom import ToolRegistry, tool


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


registry = ToolRegistry([add])
openai_tools = registry.to_openai_agents()


if __name__ == "__main__":
    print(openai_tools)
