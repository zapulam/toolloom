"""PydanticAI adapter."""

from __future__ import annotations

import inspect
from collections.abc import Iterable
from typing import Any, cast

from toolloom.spec import ToolDefinition

from ._shared import import_optional
from ._wrappers import callable_for_definition


def to_pydantic_ai(definitions: Iterable[ToolDefinition]) -> list[Any]:
    """Convert Toolloom definitions into PydanticAI `Tool` objects."""

    pydantic_ai = import_optional(
        "pydantic_ai",
        dependency="PydanticAI",
        extra="pydantic-ai",
    )
    tool_cls = cast(Any, pydantic_ai).Tool
    return [_to_pydantic_ai_tool(definition, tool_cls) for definition in definitions]


def _to_pydantic_ai_tool(definition: ToolDefinition, tool_cls: Any) -> Any:
    spec = definition.spec
    kwargs: dict[str, Any] = {}
    parameters = inspect.signature(tool_cls).parameters

    if "takes_ctx" in parameters:
        kwargs["takes_ctx"] = False
    if "name" in parameters:
        kwargs["name"] = spec.name
    if "description" in parameters:
        kwargs["description"] = spec.description
    if "metadata" in parameters:
        kwargs["metadata"] = spec.metadata
    if "timeout" in parameters:
        kwargs["timeout"] = spec.timeout

    return tool_cls(callable_for_definition(definition), **kwargs)
