from pathlib import Path

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.language_models.fake import FakeListLLM
from langchain_core.prompts import PromptTemplate

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

# Convert executable tools and markdown-backed skills, then add both to the
# LangChain agent and executor.
langchain_tools = tool_registry.to_langchain() + skill_registry.to_langchain()
llm = FakeListLLM(responses=["Final Answer: done"])
prompt = PromptTemplate.from_template(
    """Answer the question using the available tools.

Tools:
{tools}

Tool names: {tool_names}

Question: {input}
Thought:{agent_scratchpad}"""
)
langchain_agent = create_react_agent(llm, langchain_tools, prompt)
agent_executor = AgentExecutor(agent=langchain_agent, tools=langchain_tools)



if __name__ == "__main__":
    print([tool.name for tool in agent_executor.tools])
