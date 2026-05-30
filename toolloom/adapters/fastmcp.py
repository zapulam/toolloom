"""FastMCP adapter."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from toolloom.spec import ToolDefinition

from ._shared import import_optional


def to_fastmcp(
    definitions: Iterable[ToolDefinition],
    *,
    name: str = "toolloom Server",
    **kwargs: Any,
) -> Any:
    """Convert Toolloom definitions into a FastMCP server."""

    fastmcp = import_optional("fastmcp", dependency="FastMCP", extra="mcp")
    fastmcp_cls = cast(Any, fastmcp).FastMCP
    server = fastmcp_cls(name=name, **kwargs)

    for definition in definitions:
        _register_tool(server, definition)

    return server


def add_to_fastmcp(server: Any, definitions: Iterable[ToolDefinition]) -> Any:
    """Register Toolloom definitions on an existing FastMCP server."""

    for definition in definitions:
        _register_tool(server, definition)

    return server


def _register_tool(server: Any, definition: ToolDefinition) -> None:
    spec = definition.spec
    metadata = {
        **spec.metadata,
        "toolloom": {
            "side_effects": spec.side_effects,
            "destructive": spec.destructive,
            "idempotent": spec.idempotent,
            "requires_auth": spec.requires_auth,
            "experimental": spec.experimental,
        },
    }
    decorator = server.tool(
        name=spec.name,
        description=spec.description or None,
        tags=set(spec.tags),
        meta=metadata,
    )
    decorator(definition.func)
