"""Toolloom: framework-neutral tool definitions for AI agents."""

from .decorators import get_tool_definition, get_tool_spec, tool
from .errors import (
    MissingOptionalDependencyError,
    SkillExecutionError,
    SkillNotFoundError,
    SkillRegistrationError,
    SkillSchemaError,
    ToolAdapterError,
    ToolExecutionError,
    ToolloomError,
    ToolNotFoundError,
    ToolRegistrationError,
    ToolSchemaError,
    ToolTimeoutError,
    ToolValidationError,
)
from .lint import ToolLintIssue, lint_registry, lint_tool
from .registry import ToolRegistry
from .skills import SkillRegistry, get_skill_definition, get_skill_spec, skill
from .spec import SkillDefinition, SkillSpec, ToolDefinition, ToolSpec

__all__ = [
    "MissingOptionalDependencyError",
    "SkillDefinition",
    "SkillExecutionError",
    "SkillNotFoundError",
    "SkillRegistrationError",
    "SkillRegistry",
    "SkillSchemaError",
    "SkillSpec",
    "ToolAdapterError",
    "ToolDefinition",
    "ToolExecutionError",
    "ToolLintIssue",
    "ToolNotFoundError",
    "ToolRegistrationError",
    "ToolRegistry",
    "ToolSchemaError",
    "ToolSpec",
    "ToolTimeoutError",
    "ToolValidationError",
    "ToolloomError",
    "get_skill_definition",
    "get_skill_spec",
    "get_tool_definition",
    "get_tool_spec",
    "lint_registry",
    "lint_tool",
    "skill",
    "tool",
]
