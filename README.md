# Toolloom

Toolloom is a framework-neutral tool definition layer for AI agents and MCP
servers. Define a Python function as a tool once, keep its schema and metadata in
one stable contract, then export it to runtimes such as FastMCP, OpenAI Agents
SDK, LangChain, and LangGraph.

Toolloom is not trying to replace those frameworks. It gives teams one place to
declare names, descriptions, schemas, validation, runtime behavior, and metadata
such as side effects, destructive behavior, auth requirements, idempotency, and
timeouts.

## Why Not Just Use Framework Decorators?

FastMCP, OpenAI Agents SDK, and LangChain all provide good tool primitives. The
problem appears when the same tool is defined separately in each framework:
schemas drift, descriptions diverge, and framework-specific metadata becomes the
source of truth.

Toolloom keeps a serializable `ToolSpec` independent from adapters. Framework
exports are intentionally thin and may not map every metadata field perfectly,
but the canonical contract remains available inside Toolloom.

## Installation

```bash
pip install toolloom
```

Optional adapters are installed with extras:

```bash
pip install "toolloom[mcp]"
pip install "toolloom[openai]"
pip install "toolloom[langchain]"
pip install "toolloom[all]"
```

For development:

```bash
python -m pip install -e ".[dev]"
```

## Basic Usage

```python
from toolloom import ToolRegistry, get_tool_definition, get_tool_spec, tool


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


spec = get_tool_spec(search_customers)
result = get_tool_definition(search_customers).invoke({"query": "Ada"})

registry = ToolRegistry()
registry.register(search_customers)
```

The decorated function remains directly callable:

```python
search_customers("Ada", limit=5)
```

Toolloom also attaches `__toolloom_spec__` and `__toolloom_definition__`, but
public code should prefer `get_tool_spec()` and `get_tool_definition()`.

## Registry Exports

```python
mcp_server = registry.to_fastmcp(name="CRM Tools")
openai_tools = registry.to_openai_agents()
langchain_tools = registry.to_langchain()
langgraph_tools = registry.to_langgraph()
```

FastMCP uses `from fastmcp import FastMCP` and registers each callable with
`mcp.tool(...)`. LangChain uses `langchain_core.tools.StructuredTool`. LangGraph
delegates to LangChain-compatible tools and also exposes
`registry.to_langgraph_tool_node()` when `langgraph.prebuilt.ToolNode` is
installed. OpenAI Agents SDK uses `agents.FunctionTool` so Toolloom can pass its
own JSON schema and invocation wrapper.

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
