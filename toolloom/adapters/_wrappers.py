"""Callable wrappers shared by framework adapters."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, cast

from toolloom.spec import ToolDefinition


def callable_for_definition(definition: ToolDefinition) -> Callable[..., Any]:
    """Return a callable that preserves metadata while invoking through Toolloom."""

    signature = inspect.signature(definition.func)
    spec = definition.spec

    def call_arguments(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
        bound = signature.bind(*args, **kwargs)
        return dict(bound.arguments)

    wrapper: Callable[..., Any]
    if definition.is_async:

        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await definition.ainvoke(call_arguments(args, kwargs))

        wrapper = async_wrapper
    else:

        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return definition.invoke(call_arguments(args, kwargs))

        wrapper = sync_wrapper

    wrapper.__name__ = spec.name
    wrapper.__doc__ = spec.description
    cast(Any, wrapper).__signature__ = signature
    return wrapper
