"""LangGraph adapter."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from toolloom.spec import ToolDefinition

from ._shared import import_optional
from .langchain import to_langchain


def to_langgraph(definitions: Iterable[ToolDefinition]) -> list[Any]:
    """Return LangGraph-compatible tools.

    LangGraph's prebuilt tool execution works with LangChain tools, so the MVP
    delegates to the LangChain adapter.
    """

    return to_langchain(definitions)


def to_langgraph_tool_node(definitions: Iterable[ToolDefinition], **kwargs: Any) -> Any:
    """Convert Toolloom definitions into a LangGraph `ToolNode`."""

    prebuilt = import_optional("langgraph.prebuilt", dependency="LangGraph", extra="langchain")
    tool_node = cast(Any, prebuilt).ToolNode
    return tool_node(to_langchain(definitions), **kwargs)
