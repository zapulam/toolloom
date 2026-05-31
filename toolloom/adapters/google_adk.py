"""Google Agent Development Kit adapter."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from toolloom.spec import ToolDefinition

from ._shared import import_optional
from ._wrappers import callable_for_definition


def to_google_adk(definitions: Iterable[ToolDefinition]) -> list[Any]:
    """Convert Toolloom definitions into Google ADK `FunctionTool` objects."""

    tools_module = import_optional(
        "google.adk.tools",
        dependency="Google ADK",
        extra="google-adk",
    )
    function_tool = cast(Any, tools_module).FunctionTool
    return [function_tool(callable_for_definition(definition)) for definition in definitions]
