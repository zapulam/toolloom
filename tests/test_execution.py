from __future__ import annotations

import asyncio
import time

import pytest

from toolloom import get_tool_definition, tool
from toolloom.errors import ToolExecutionError, ToolTimeoutError, ToolValidationError


def test_sync_invocation_validates_and_calls_function() -> None:
    @tool
    def add(a: int, b: int = 1) -> int:
        """Add two numbers."""
        return a + b

    definition = get_tool_definition(add)

    assert definition.invoke({"a": 2}) == 3


@pytest.mark.asyncio
async def test_async_invocation_validates_and_awaits_function() -> None:
    @tool
    async def add(a: int, b: int) -> int:
        """Add two numbers asynchronously."""
        await asyncio.sleep(0)
        return a + b

    definition = get_tool_definition(add)

    assert await definition.ainvoke({"a": 2, "b": 3}) == 5


def test_validation_failure_raises_custom_error() -> None:
    @tool
    def add(a: int) -> int:
        """Add one."""
        return a + 1

    with pytest.raises(ToolValidationError):
        get_tool_definition(add).invoke({"a": "not-int"})


def test_execution_failure_is_wrapped() -> None:
    @tool
    def fail() -> int:
        """Fail intentionally."""
        raise RuntimeError("boom")

    with pytest.raises(ToolExecutionError, match="boom"):
        get_tool_definition(fail).invoke({})


def test_sync_invoke_rejects_async_tool() -> None:
    @tool
    async def async_tool() -> str:
        """Async only."""
        return "ok"

    with pytest.raises(ToolExecutionError, match="ainvoke"):
        get_tool_definition(async_tool).invoke({})


@pytest.mark.asyncio
async def test_timeout_behavior_for_async_tool() -> None:
    @tool(timeout=0.01)
    async def slow() -> str:
        """Slow async tool."""
        await asyncio.sleep(0.05)
        return "done"

    with pytest.raises(ToolTimeoutError):
        await get_tool_definition(slow).ainvoke({})


def test_timeout_behavior_for_sync_tool() -> None:
    @tool(timeout=0.01)
    def slow() -> str:
        """Slow sync tool."""
        time.sleep(0.05)
        return "done"

    with pytest.raises(ToolTimeoutError):
        get_tool_definition(slow).invoke({})
