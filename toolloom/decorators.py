"""The public `@tool` decorator and spec lookup helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, overload

from .errors import ToolSchemaError
from .introspection import create_tool_definition
from .spec import ToolDefinition, ToolSpec

F = TypeVar("F", bound=Callable[..., Any])

TOOL_DEFINITION_ATTR = "__toolloom_definition__"
TOOL_SPEC_ATTR = "__toolloom_spec__"


@overload
def tool(func: F, /) -> F: ...


@overload
def tool(
    func: None = None,
    /,
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
) -> Callable[[F], F]: ...


def tool(
    func: F | None = None,
    /,
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
) -> F | Callable[[F], F]:
    """Decorate a Python callable as a Toolloom tool while preserving callability."""

    def decorate(target: F) -> F:
        definition = create_tool_definition(
            target,
            name=name,
            description=description,
            tags=tags,
            side_effects=side_effects,
            destructive=destructive,
            idempotent=idempotent,
            requires_auth=requires_auth,
            timeout=timeout,
            experimental=experimental,
            metadata=metadata,
        )
        setattr(target, TOOL_DEFINITION_ATTR, definition)
        setattr(target, TOOL_SPEC_ATTR, definition.spec)
        return target

    if func is not None:
        return decorate(func)
    return decorate


def get_tool_definition(value: Callable[..., Any] | ToolDefinition) -> ToolDefinition:
    """Return a `ToolDefinition` for a decorated function or definition."""

    if isinstance(value, ToolDefinition):
        return value

    definition = getattr(value, TOOL_DEFINITION_ATTR, None)
    if isinstance(definition, ToolDefinition):
        return definition

    if callable(value):
        return create_tool_definition(value)

    raise ToolSchemaError(f"Object {value!r} is not a Toolloom tool or callable.")


def get_tool_spec(value: Callable[..., Any] | ToolDefinition | ToolSpec) -> ToolSpec:
    """Return a `ToolSpec` without requiring users to access implementation attributes."""

    if isinstance(value, ToolSpec):
        return value
    if isinstance(value, ToolDefinition):
        return value.spec

    spec = getattr(value, TOOL_SPEC_ATTR, None)
    if isinstance(spec, ToolSpec):
        return spec

    return get_tool_definition(value).spec
