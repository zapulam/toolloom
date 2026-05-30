"""Framework-neutral tool specifications and executable definitions."""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .errors import ToolExecutionError, ToolTimeoutError, ToolValidationError


class ToolSpec(BaseModel):
    """Serializable, framework-neutral description of an AI tool."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    parameters_schema: dict[str, Any]
    return_schema: dict[str, Any] | None = None
    tags: list[str] = Field(default_factory=list)
    side_effects: bool = False
    destructive: bool = False
    idempotent: bool | None = None
    requires_auth: bool = False
    timeout: float | None = None
    experimental: bool = False
    callable_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """A `ToolSpec` paired with the Python callable that implements it."""

    spec: ToolSpec
    func: Callable[..., Any]
    input_model: type[BaseModel]

    @property
    def is_async(self) -> bool:
        """Whether the underlying callable is asynchronous."""

        return inspect.iscoroutinefunction(self.func)

    def validate_input(self, arguments: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Validate raw arguments and return keyword arguments for the callable."""

        payload: Mapping[str, Any] = {} if arguments is None else arguments
        if not isinstance(payload, Mapping):
            raise ToolValidationError("Tool input must be a mapping of argument names to values.")

        try:
            validated = self.input_model.model_validate(dict(payload))
        except ValidationError as exc:
            raise ToolValidationError(str(exc)) from exc

        return {name: getattr(validated, name) for name in self.input_model.model_fields}

    def invoke(self, arguments: Mapping[str, Any] | None = None) -> Any:
        """Synchronously validate and invoke the tool."""

        if self.is_async:
            raise ToolExecutionError(
                f"Tool '{self.spec.name}' is async and must be called with ainvoke()."
            )

        kwargs = self.validate_input(arguments)
        try:
            if self.spec.timeout is None:
                return self.func(**kwargs)
            return self._invoke_sync_with_timeout(kwargs)
        except ToolTimeoutError:
            raise
        except Exception as exc:
            raise ToolExecutionError(f"Tool '{self.spec.name}' failed: {exc}") from exc

    async def ainvoke(self, arguments: Mapping[str, Any] | None = None) -> Any:
        """Asynchronously validate and invoke the tool."""

        kwargs = self.validate_input(arguments)
        try:
            if self.is_async:
                coroutine = self.func(**kwargs)
                if self.spec.timeout is None:
                    return await coroutine
                return await asyncio.wait_for(coroutine, timeout=self.spec.timeout)

            if self.spec.timeout is None:
                return self.func(**kwargs)
            return await asyncio.wait_for(
                asyncio.to_thread(self.func, **kwargs),
                timeout=self.spec.timeout,
            )
        except TimeoutError as exc:
            raise ToolTimeoutError(f"Tool '{self.spec.name}' timed out.") from exc
        except ToolTimeoutError:
            raise
        except Exception as exc:
            raise ToolExecutionError(f"Tool '{self.spec.name}' failed: {exc}") from exc

    def _invoke_sync_with_timeout(self, kwargs: dict[str, Any]) -> Any:
        timeout = self.spec.timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.func, **kwargs)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError as exc:
                future.cancel()
                raise ToolTimeoutError(f"Tool '{self.spec.name}' timed out.") from exc
