from pathlib import Path
from typing import Any

from toolloom import MissingOptionalDependencyError, SkillRegistry, ToolRegistry, skill, tool

try:
    from langgraph.prebuilt import ToolNode, create_react_agent
except ImportError:
    ToolNode = None
    create_react_agent = None

SKILL_PATH = Path(__file__).with_name("skills") / "math_strategy.md"


@tool(description="Add two integers and return the total.")
def add(a: int, b: int) -> int:
    return a + b


@skill(
    description="Read the math strategy instructions for the agent.",
    markdown_path=str(SKILL_PATH),
)
def math_strategy() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


tool_registry = ToolRegistry([add])
skill_registry = SkillRegistry([math_strategy])

# Convert executable tools and markdown-backed skills, then add both to
# LangGraph's tool execution node. `build_langgraph_agent()` shows the same
# combined list being attached to a LangGraph agent when a model is available.
langgraph_tools = tool_registry.to_langgraph() + skill_registry.to_langgraph()
tool_node = ToolNode(langgraph_tools) if ToolNode is not None else None


def build_langgraph_agent(model: Any) -> Any:
    if create_react_agent is None:
        raise MissingOptionalDependencyError("LangGraph", "langchain")
    return create_react_agent(model=model, tools=langgraph_tools)


if __name__ == "__main__":
    print([tool.name for tool in langgraph_tools])
    print(tool_node)
