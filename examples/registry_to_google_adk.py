from pathlib import Path

from google.adk.agents import Agent

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

# Convert tools and skills into Google ADK FunctionTool objects, then add all of
# them to the Agent.
adk_tools = tool_registry.to_google_adk() + skill_registry.to_google_adk()
agent = Agent(
    name="math_agent",
    model="gemini-2.0-flash",
    instruction="Use tools for calculations and skills for markdown guidance.",
    tools=adk_tools,
)


if __name__ == "__main__":
    print([tool.name for tool in adk_tools])
