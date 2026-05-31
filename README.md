<p align="center">
  <img src=".assets/toolloom.png" alt="Toolloom logo" width="812">
</p>

<p align="center">
  <strong>Define AI tools once. Export them everywhere.</strong>
</p>

<p align="center">
  A framework-neutral tool contract for Python agents, MCP servers, and fast-moving
  LLM runtimes.
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-blue"></a>
  <a href="https://docs.pydantic.dev/latest/"><img alt="Pydantic v2" src="https://img.shields.io/badge/pydantic-v2-e92063"></a>
  <a href="#development"><img alt="pytest" src="https://img.shields.io/badge/tests-pytest-0a9edc"></a>
  <a href="#development"><img alt="Ruff" src="https://img.shields.io/badge/lint-ruff-261230"></a>
  <a href="#development"><img alt="mypy" src="https://img.shields.io/badge/types-mypy-2a6db2"></a>
  <a href="#installation"><img alt="Adapters" src="https://img.shields.io/badge/adapters-FastMCP%20%7C%20OpenAI%20%7C%20LangChain%20%7C%20LangGraph%20%7C%20PydanticAI%20%7C%20CrewAI%20%7C%20Google%20ADK-4b5563"></a>
  <a href="#license"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green"></a>
</p>

---

Toolloom turns Python callables plus metadata into stable, serializable tool and
skill contracts. Those contracts stay independent of any one agent framework,
while thin adapters export them to FastMCP, OpenAI Agents SDK, LangChain,
LangGraph, PydanticAI, CrewAI, and Google ADK.

It is built for teams that want one canonical place for tool names,
descriptions, schemas, validation, runtime behavior, errors, safety metadata,
and adapter exports.

<table>
  <tr>
    <td width="25%">
      <strong>Define once</strong><br>
      Decorate a Python function and keep one canonical <code>ToolSpec</code>.
    </td>
    <td width="25%">
      <strong>Validate before execution</strong><br>
      Generate Pydantic v2 schemas and validate inputs before tools run.
    </td>
    <td width="25%">
      <strong>Export to frameworks</strong><br>
      Bridge to FastMCP, OpenAI Agents SDK, LangChain, LangGraph, PydanticAI,
      CrewAI, and Google ADK.
    </td>
    <td width="25%">
      <strong>Lint tool quality</strong><br>
      Catch weak descriptions, vague parameters, and unsafe metadata drift.
    </td>
  </tr>
</table>

## What You Get

- A pleasant `@tool` decorator that preserves the original function's callability.
- A serializable `ToolSpec` for names, descriptions, schemas, return types, tags,
  auth, timeouts, idempotency, side effects, and arbitrary metadata.
- A `ToolDefinition` wrapper for validated sync and async invocation.
- A `ToolRegistry` for grouping tools and exporting them to optional adapters.
- A `@skill` decorator and `SkillRegistry` for markdown-backed agent guidance.
- Non-blocking quality linting for tool descriptions, type hints, naming, and
  safety metadata.

## Why Toolloom?

FastMCP, OpenAI Agents SDK, LangChain, LangGraph, PydanticAI, CrewAI, and Google
ADK all provide useful tool primitives. The problem starts when the same business
action is declared separately in every runtime: schemas drift, descriptions
diverge, and framework-specific wrappers become the accidental source of truth.

Toolloom makes the tool and skill contracts the source of truth. Tools are typed
functions agents can execute. Skills are zero-argument functions that return
markdown instructions agents can read. Framework adapters are intentionally thin,
so integrations can evolve without rewriting your core definitions.

## Installation

The base package only installs Toolloom's framework-neutral core and Pydantic v2:

```bash
pip install toolloom
```

Install optional integrations only when you need them:

```bash
pip install "toolloom[mcp]"
pip install "toolloom[openai]"
pip install "toolloom[langchain]"
pip install "toolloom[pydantic-ai]"
pip install "toolloom[crewai]"
pip install "toolloom[google-adk]"
pip install "toolloom[all]"
```

For development:

```bash
python -m pip install -e ".[dev]"
```

## Quick Start

```python
from toolloom import SkillRegistry, ToolRegistry, get_tool_definition, get_tool_spec, skill, tool


@tool(
    name="search_customers",
    description="Search customers by name, email, or account ID.",
    tags=["crm", "read-only"],
    side_effects=False,
    timeout=10,
)
def search_customers(query: str, limit: int = 10) -> list[dict]:
    """Search the CRM for customer records."""
    return []


@skill(
    name="customer_research_playbook",
    description="Read the markdown playbook for customer research tasks.",
    markdown_path="skills/customer_research.md",
)
def customer_research_playbook() -> str:
    return "# Customer research\n\nCheck account status before drafting outreach."


spec = get_tool_spec(search_customers)
result = get_tool_definition(search_customers).invoke({"query": "Ada"})

registry = ToolRegistry()
registry.register(search_customers)

skills = SkillRegistry([customer_research_playbook])
```

The decorated function remains directly callable, so adopting Toolloom does not
change ordinary Python usage:

```python
search_customers("Ada", limit=5)
```

Toolloom also attaches implementation attributes for tools and skills, but public
code should prefer helper functions such as `get_tool_spec()` and registry APIs.

## Export Targets

`ToolRegistry` is the source-of-truth collection for executable functions.
`SkillRegistry` is the source-of-truth collection for markdown-backed guidance.
Frameworks should receive the output of adapter methods, not registry objects
themselves:

This means using `registry.to_fastmcp()` instead of `FastMCP(tools=registry)`,
and `Agent(..., tools=registry.to_openai_agents())` instead of
`Agent(..., tools=registry)`.

```python
tool_registry = ToolRegistry([search_customers])
skill_registry = SkillRegistry([customer_research_playbook])
```

For example, add both executable tools and markdown skills to each framework's
native API:

```python
from agents import Agent

openai_tools = tool_registry.to_openai_agents() + skill_registry.to_openai_agents()
agent = Agent(
    name="CRM Agent",
    tools=openai_tools,
)
```

```python
# `to_fastmcp()` creates the FastMCP app and adds executable tools.
mcp_server = tool_registry.to_fastmcp(name="CRM Tools")
skill_registry.add_to_fastmcp(mcp_server)
mcp_server.run()
```

```python
from langchain.agents import AgentExecutor, create_react_agent

langchain_tools = tool_registry.to_langchain() + skill_registry.to_langchain()
langchain_agent = create_react_agent(llm, langchain_tools, prompt)
agent_executor = AgentExecutor(agent=langchain_agent, tools=langchain_tools)
```

```python
from langgraph.prebuilt import ToolNode, create_react_agent

langgraph_tools = tool_registry.to_langgraph() + skill_registry.to_langgraph()
langgraph_agent = create_react_agent(model=model, tools=langgraph_tools)
tool_node = ToolNode(langgraph_tools)
```

```python
from pydantic_ai import Agent

pydantic_ai_tools = tool_registry.to_pydantic_ai() + skill_registry.to_pydantic_ai()
agent = Agent("openai:gpt-4o-mini", tools=pydantic_ai_tools)
```

```python
from crewai import Agent

crewai_tools = tool_registry.to_crewai() + skill_registry.to_crewai()
agent = Agent(
    role="CRM Agent",
    goal="Research customers and follow the markdown playbook.",
    backstory="You use Toolloom tools for actions and Toolloom skills for guidance.",
    tools=crewai_tools,
)
```

```python
from google.adk.agents import Agent

adk_tools = tool_registry.to_google_adk() + skill_registry.to_google_adk()
agent = Agent(
    name="crm_agent",
    model="gemini-2.0-flash",
    instruction="Use tools for actions and skills for guidance.",
    tools=adk_tools,
)
```

<table>
  <tr>
    <th>Target</th>
    <th>Install extra</th>
    <th>Adapter behavior</th>
  </tr>
  <tr>
    <td>FastMCP / MCP</td>
    <td><code>toolloom[mcp]</code></td>
    <td>Creates a <code>FastMCP</code> server and registers tools plus skill readers.</td>
  </tr>
  <tr>
    <td>OpenAI Agents SDK</td>
    <td><code>toolloom[openai]</code></td>
    <td>Builds <code>agents.FunctionTool</code> objects for tools and skills.</td>
  </tr>
  <tr>
    <td>LangChain</td>
    <td><code>toolloom[langchain]</code></td>
    <td>Exports <code>langchain_core.tools.StructuredTool</code> instances.</td>
  </tr>
  <tr>
    <td>LangGraph</td>
    <td><code>toolloom[langchain]</code></td>
    <td>Returns LangChain-compatible tools or a <code>ToolNode</code>.</td>
  </tr>
  <tr>
    <td>PydanticAI</td>
    <td><code>toolloom[pydantic-ai]</code></td>
    <td>Builds <code>pydantic_ai.Tool</code> objects for tools and skills.</td>
  </tr>
  <tr>
    <td>CrewAI</td>
    <td><code>toolloom[crewai]</code></td>
    <td>Builds CrewAI <code>BaseTool</code> objects for tools and skills.</td>
  </tr>
  <tr>
    <td>Google ADK</td>
    <td><code>toolloom[google-adk]</code></td>
    <td>Builds Google ADK <code>FunctionTool</code> objects for tools and skills.</td>
  </tr>
</table>

FastMCP uses `from fastmcp import FastMCP` internally and registers each callable
with `mcp.tool(...)`. OpenAI Agents SDK exports are `agents.FunctionTool`
instances, so executable tools and markdown skills can be passed together as
`Agent(..., tools=tool_registry.to_openai_agents() + skill_registry.to_openai_agents())`.
LangChain exports are `langchain_core.tools.StructuredTool` instances. LangGraph
delegates to LangChain-compatible tools and also exposes
`registry.to_langgraph_tool_node()` for tool registries and
`skill_registry.to_langgraph_tool_node()` for skill registries when
`langgraph.prebuilt.ToolNode` is installed. PydanticAI exports
`pydantic_ai.Tool` objects. CrewAI exports `crewai.tools.BaseTool` instances.
Google ADK exports `google.adk.tools.FunctionTool` objects.

If an optional dependency is missing, adapters raise `MissingOptionalDependencyError`
with an install command.

## Linting

```python
from toolloom import lint_registry, lint_tool

issues = lint_tool(search_customers)
registry_issues = lint_registry(registry)
```

Initial lint rules check for missing or weak descriptions, missing type hints,
vague parameter names, inconsistent side-effect metadata, generic tool names,
missing return types, and oversized signatures.

## Design Principles

- Keep the core independent from any one agent framework.
- Treat schemas and safety metadata as first-class tool contract fields.
- Make optional integrations lazy so `import toolloom` stays lightweight.
- Preserve normal Python callability and avoid hidden registration side effects.
- Prefer clear errors over pretending every Python type maps cleanly to every
  downstream runtime.

## CLI

```bash
toolloom inspect path.to.module:registry
toolloom lint path.to.module:registry
```

Targets can be either a `ToolRegistry` or a single callable.

## Current Limitations

- Toolloom supports a practical subset of Python signatures: explicit parameters
  callable by keyword. Positional-only arguments, `*args`, and `**kwargs` are not
  supported.
- Complex Python types depend on what Pydantic v2 can express as JSON Schema.
- Adapter behavior is intentionally thin. Some Toolloom metadata has no direct
  equivalent in downstream frameworks and is preserved in Toolloom rather than
  forced into incompatible concepts.
- Synchronous timeout handling uses a worker thread and cannot forcibly stop
  arbitrary blocking native code.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m mypy toolloom
```

Adapter tests are skipped unless their optional dependencies are installed.

## Roadmap

- Richer docstring parsing for parameter descriptions.
- More adapter-specific metadata mapping.
- Better strict JSON Schema controls for providers that require them.
- Optional CLI command to serve a registry as FastMCP.
- CI matrix for base install and optional adapter extras.

## License

Toolloom is distributed under the MIT License.
