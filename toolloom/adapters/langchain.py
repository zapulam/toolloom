"""LangChain adapter."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from toolloom.spec import ToolDefinition

from ._shared import import_optional


def to_langchain(definitions: Iterable[ToolDefinition]) -> list[Any]:
    """Convert Toolloom definitions into LangChain `StructuredTool` objects."""

    tools_module = import_optional(
        "langchain_core.tools",
        dependency="LangChain",
        extra="langchain",
    )
    structured_tool = cast(Any, tools_module).StructuredTool
    return [_to_langchain_tool(definition, structured_tool) for definition in definitions]


def _to_langchain_tool(definition: ToolDefinition, structured_tool: Any) -> Any:
    spec = definition.spec

    def sync_wrapper(**kwargs: Any) -> Any:
        return definition.invoke(kwargs)

    async def async_wrapper(**kwargs: Any) -> Any:
        return await definition.ainvoke(kwargs)

    sync_wrapper.__name__ = spec.name
    sync_wrapper.__doc__ = spec.description
    async_wrapper.__name__ = spec.name
    async_wrapper.__doc__ = spec.description

    kwargs: dict[str, Any] = {
        "name": spec.name,
        "description": spec.description or f"Toolloom tool {spec.name}.",
        "args_schema": definition.input_model,
        "infer_schema": False,
    }
    if definition.is_async:
        kwargs["coroutine"] = async_wrapper
    else:
        kwargs["func"] = sync_wrapper
        kwargs["coroutine"] = async_wrapper

    return structured_tool.from_function(**kwargs)
