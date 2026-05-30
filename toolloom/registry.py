"""Tool registry and adapter export methods."""

from __future__ import annotations

import builtins
from collections.abc import Callable, Iterable
from typing import Any

from .decorators import get_tool_definition
from .errors import ToolNotFoundError, ToolRegistrationError
from .spec import ToolDefinition


class ToolRegistry:
    """A named collection of Toolloom tool definitions."""

    def __init__(self, tools: Iterable[Callable[..., Any] | ToolDefinition] | None = None) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        if tools is not None:
            self.register_many(tools)

    def register(
        self,
        value: Callable[..., Any] | ToolDefinition,
        *,
        replace: bool = False,
    ) -> ToolDefinition:
        """Register one tool and return its definition."""

        definition = get_tool_definition(value)
        name = definition.spec.name
        if name in self._tools and not replace:
            raise ToolRegistrationError(
                f"Tool '{name}' is already registered. Pass replace=True to overwrite it."
            )
        self._tools[name] = definition
        return definition

    def register_many(
        self,
        values: Iterable[Callable[..., Any] | ToolDefinition],
        *,
        replace: bool = False,
    ) -> None:
        """Register multiple tools."""

        for value in values:
            self.register(value, replace=replace)

    def get(self, name: str) -> ToolDefinition:
        """Return a registered tool by name."""

        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(name) from exc

    def list(self) -> builtins.list[ToolDefinition]:
        """Return registered tools in insertion order."""

        return list(self._tools.values())

    def names(self) -> builtins.list[str]:
        """Return registered tool names in insertion order."""

        return list(self._tools)

    def to_fastmcp(self, name: str = "toolloom Server", **kwargs: Any) -> Any:
        """Export the registry to a FastMCP server."""

        from .adapters.fastmcp import to_fastmcp

        return to_fastmcp(self.list(), name=name, **kwargs)

    def to_openai_agents(self) -> builtins.list[Any]:
        """Export the registry to OpenAI Agents SDK tools."""

        from .adapters.openai_agents import to_openai_agents

        return to_openai_agents(self.list())

    def to_langchain(self) -> builtins.list[Any]:
        """Export the registry to LangChain tools."""

        from .adapters.langchain import to_langchain

        return to_langchain(self.list())

    def to_langgraph(self) -> builtins.list[Any]:
        """Export the registry to LangGraph-compatible LangChain tools."""

        from .adapters.langgraph import to_langgraph

        return to_langgraph(self.list())

    def to_langgraph_tool_node(self, **kwargs: Any) -> Any:
        """Export the registry to a LangGraph ToolNode."""

        from .adapters.langgraph import to_langgraph_tool_node

        return to_langgraph_tool_node(self.list(), **kwargs)
