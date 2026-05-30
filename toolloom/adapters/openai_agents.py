"""OpenAI Agents SDK adapter."""

from __future__ import annotations

import inspect
import json
from collections.abc import Iterable
from typing import Any, cast

from toolloom.spec import ToolDefinition

from ._shared import import_optional


def to_openai_agents(definitions: Iterable[ToolDefinition]) -> list[Any]:
    """Convert Toolloom definitions into OpenAI Agents SDK `FunctionTool` objects."""

    agents = import_optional("agents", dependency="OpenAI Agents SDK", extra="openai")
    function_tool_cls = cast(Any, agents).FunctionTool
    return [_to_openai_tool(definition, function_tool_cls) for definition in definitions]


def _to_openai_tool(definition: ToolDefinition, function_tool_cls: Any) -> Any:
    spec = definition.spec

    async def on_invoke_tool(_context: Any, arguments_json: str) -> Any:
        arguments = json.loads(arguments_json or "{}")
        return await definition.ainvoke(arguments)

    kwargs: dict[str, Any] = {
        "name": spec.name,
        "description": spec.description,
        "params_json_schema": spec.parameters_schema,
        "on_invoke_tool": on_invoke_tool,
    }

    signature = inspect.signature(function_tool_cls)
    if "strict_json_schema" in signature.parameters:
        kwargs["strict_json_schema"] = False

    return function_tool_cls(**kwargs)
