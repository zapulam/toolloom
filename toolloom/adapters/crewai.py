"""CrewAI adapter."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from pydantic import BaseModel

from toolloom.spec import ToolDefinition

from ._shared import import_optional


def to_crewai(definitions: Iterable[ToolDefinition]) -> list[Any]:
    """Convert Toolloom definitions into CrewAI `BaseTool` objects."""

    tools_module = import_optional("crewai.tools", dependency="CrewAI", extra="crewai")
    base_tool = cast(Any, tools_module).BaseTool
    return [_to_crewai_tool(definition, base_tool) for definition in definitions]


def _to_crewai_tool(definition: ToolDefinition, base_tool: Any) -> Any:
    spec = definition.spec

    def _run(self: Any, **kwargs: Any) -> Any:
        return definition.invoke(kwargs)

    async def _arun(self: Any, **kwargs: Any) -> Any:
        return await definition.ainvoke(kwargs)

    tool_class = type(
        f"{_pascal_case(spec.name)}CrewAITool",
        (base_tool,),
        {
            "__annotations__": {
                "name": str,
                "description": str,
                "args_schema": type[BaseModel],
            },
            "name": spec.name,
            "description": spec.description or f"Toolloom tool {spec.name}.",
            "args_schema": definition.input_model,
            "_run": _run,
            "_arun": _arun,
        },
    )
    return tool_class()


def _pascal_case(value: str) -> str:
    parts = value.replace("-", "_").split("_")
    return "".join(part.capitalize() for part in parts if part) or "Tool"
