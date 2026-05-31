from pathlib import Path

from crewai import Agent

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

# Convert tools and skills into CrewAI BaseTool objects, then add all of them
# to the Agent.
crewai_tools = tool_registry.to_crewai() + skill_registry.to_crewai()
agent = Agent(
    role="Math Agent",
    goal="Solve arithmetic tasks and explain the strategy used.",
    backstory="You use Toolloom tools for calculations and Toolloom skills for guidance.",
    tools=crewai_tools,
)


if __name__ == "__main__":
    print([tool.name for tool in agent.tools])
