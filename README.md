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
  <a href="#installation"><img alt="Adapters" src="https://img.shields.io/badge/adapters-FastMCP%20%7C%20OpenAI%20%7C%20LangChain%20%7C%20LangGraph-4b5563"></a>
  <a href="#license"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green"></a>
</p>

---

Toolloom turns a Python callable plus metadata into a stable, serializable
`ToolSpec`. That spec stays independent of any one agent framework, while thin
adapters export it to FastMCP, OpenAI Agents SDK, LangChain, and LangGraph.

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
      Bridge to FastMCP, OpenAI Agents SDK, LangChain, and LangGraph.
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
- Non-blocking quality linting for tool descriptions, type hints, naming, and
  safety metadata.

## Why Toolloom?

FastMCP, OpenAI Agents SDK, LangChain, and LangGraph all provide useful tool
primitives. The problem starts when the same business action is declared
separately in every runtime: schemas drift, descriptions diverge, and
framework-specific wrappers become the accidental source of truth.

Toolloom makes the tool contract the source of truth. Framework adapters are
intentionally thin, so integrations can evolve without rewriting your core tool
definitions.

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
pip install "toolloom[all]"
```

For development:

```bash
python -m pip install -e ".[dev]"
```

## Quick Start

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

The decorated function remains directly callable, so adopting Toolloom does not
change ordinary Python usage:

```python
search_customers("Ada", limit=5)
```

Toolloom also attaches `__toolloom_spec__` and `__toolloom_definition__`, but
public code should prefer `get_tool_spec()` and `get_tool_definition()`.

## Export Targets

```python
mcp_server = registry.to_fastmcp(name="CRM Tools")
openai_tools = registry.to_openai_agents()
langchain_tools = registry.to_langchain()
langgraph_tools = registry.to_langgraph()
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
    <td>Creates a <code>FastMCP</code> server and registers Toolloom callables.</td>
  </tr>
  <tr>
    <td>OpenAI Agents SDK</td>
    <td><code>toolloom[openai]</code></td>
    <td>Builds <code>agents.FunctionTool</code> objects from Toolloom schemas.</td>
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
</table>

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
