"""Non-blocking quality checks for Toolloom tools."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, Literal, get_type_hints

from pydantic import BaseModel, ConfigDict

from .decorators import get_tool_definition
from .registry import ToolRegistry
from .spec import ToolDefinition

Severity = Literal["info", "warning", "error"]

VAGUE_PARAMETER_NAMES = {"x", "y", "z", "data", "input", "payload", "args", "kwargs"}
GENERIC_TOOL_NAMES = {"run", "call", "process", "execute", "handle", "do"}


class ToolLintIssue(BaseModel):
    """A lint issue found in a tool definition."""

    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    severity: Severity
    tool_name: str | None = None
    field: str | None = None


def lint_tool(value: Callable[..., Any] | ToolDefinition) -> list[ToolLintIssue]:
    """Return non-blocking quality issues for a tool."""

    definition = get_tool_definition(value)
    spec = definition.spec
    issues: list[ToolLintIssue] = []
    description = spec.description.strip()
    normalized_name = spec.name.replace("_", " ").strip().lower()

    if not description:
        issues.append(
            _issue("missing-description", "Tool is missing a description.", "error", spec.name)
        )
    elif len(description) < 20:
        issues.append(
            _issue(
                "description-too-short",
                "Tool description is too short to guide an agent reliably.",
                "warning",
                spec.name,
                "description",
            )
        )

    repeats_name = description.strip().lower().rstrip(".") in {
        spec.name.lower(),
        normalized_name,
    }
    if description and repeats_name:
        issues.append(
            _issue(
                "description-repeats-name",
                "Tool description repeats the name without explaining behavior.",
                "warning",
                spec.name,
                "description",
            )
        )

    if spec.name.lower() in GENERIC_TOOL_NAMES:
        issues.append(
            _issue(
                "generic-tool-name",
                "Tool name is too generic for reliable agent tool selection.",
                "warning",
                spec.name,
                "name",
            )
        )

    if spec.destructive and not spec.side_effects:
        issues.append(
            _issue(
                "destructive-without-side-effects",
                "Tool is marked destructive but not side-effecting.",
                "error",
                spec.name,
                "destructive",
            )
        )

    if spec.side_effects and spec.idempotent is None:
        issues.append(
            _issue(
                "side-effects-idempotency-unknown",
                "Tool has side effects but idempotency is unspecified.",
                "warning",
                spec.name,
                "idempotent",
            )
        )

    signature = inspect.signature(definition.func)
    hints = get_type_hints(definition.func, include_extras=True)
    if len(signature.parameters) > 8:
        issues.append(
            _issue(
                "too-many-parameters",
                "Tool has many parameters; consider a structured input model.",
                "warning",
                spec.name,
            )
        )

    properties = spec.parameters_schema.get("properties", {})
    for parameter in signature.parameters.values():
        if parameter.name not in hints:
            issues.append(
                _issue(
                    "missing-parameter-type",
                    f"Parameter '{parameter.name}' is missing a type hint.",
                    "error",
                    spec.name,
                    parameter.name,
                )
            )
        parameter_description = properties.get(parameter.name, {}).get("description")
        if parameter.name.lower() in VAGUE_PARAMETER_NAMES and not parameter_description:
            issues.append(
                _issue(
                    "vague-parameter-name",
                    f"Parameter '{parameter.name}' is vague and lacks a description.",
                    "warning",
                    spec.name,
                    parameter.name,
                )
            )

    if "return" not in hints:
        issues.append(
            _issue(
                "missing-return-type",
                "Tool is missing a return type annotation.",
                "warning",
                spec.name,
                "return",
            )
        )

    return issues


def lint_registry(registry: ToolRegistry) -> list[ToolLintIssue]:
    """Return lint issues for every tool in a registry."""

    return [issue for definition in registry.list() for issue in lint_tool(definition)]


def _issue(
    code: str,
    message: str,
    severity: Severity,
    tool_name: str | None,
    field: str | None = None,
) -> ToolLintIssue:
    return ToolLintIssue(
        code=code,
        message=message,
        severity=severity,
        tool_name=tool_name,
        field=field,
    )
