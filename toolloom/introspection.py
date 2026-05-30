"""Callable introspection for Toolloom tool definitions."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

from .schema import build_input_model, parameter_schema, return_schema
from .spec import ToolDefinition, ToolSpec


def create_tool_definition(
    func: Callable[..., Any],
    *,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    side_effects: bool = False,
    destructive: bool = False,
    idempotent: bool | None = None,
    requires_auth: bool = False,
    timeout: float | None = None,
    experimental: bool = False,
    metadata: dict[str, Any] | None = None,
) -> ToolDefinition:
    """Create a `ToolDefinition` from a Python callable and Toolloom metadata."""

    tool_name = name or func.__name__
    input_model = build_input_model(func, name=f"{_pascal_case(tool_name)}Input")
    spec = ToolSpec(
        name=tool_name,
        description=description if description is not None else (inspect.getdoc(func) or ""),
        parameters_schema=parameter_schema(input_model),
        return_schema=return_schema(func),
        tags=list(tags or []),
        side_effects=side_effects,
        destructive=destructive,
        idempotent=idempotent,
        requires_auth=requires_auth,
        timeout=timeout,
        experimental=experimental,
        callable_path=callable_path(func),
        metadata=dict(metadata or {}),
    )
    return ToolDefinition(spec=spec, func=func, input_model=input_model)


def callable_path(func: Callable[..., Any]) -> str | None:
    """Return a best-effort import path for a callable."""

    module = getattr(func, "__module__", None)
    qualname = getattr(func, "__qualname__", None)
    if not module or not qualname:
        return None
    return f"{module}:{qualname}"


def _pascal_case(value: str) -> str:
    parts = value.replace("-", "_").split("_")
    return "".join(part.capitalize() for part in parts if part) or "Tool"
