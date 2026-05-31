from pathlib import Path

from pydantic_ai import Agent

from toolloom import SkillRegistry, ToolRegistry, skill, tool

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

# Convert tools and skills into PydanticAI Tool objects, then add all of them
# to the Agent.
pydantic_ai_tools = tool_registry.to_pydantic_ai() + skill_registry.to_pydantic_ai()
agent = Agent(
    "openai:gpt-4o-mini",
    tools=pydantic_ai_tools,
)


if __name__ == "__main__":
    print([tool.name for tool in pydantic_ai_tools])
