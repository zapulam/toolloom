"""Markdown-backed skill definitions and registries."""

from __future__ import annotations

import builtins
import inspect
from collections.abc import Callable, Iterable
from typing import Any, TypeVar, cast, overload

from .errors import SkillNotFoundError, SkillRegistrationError, SkillSchemaError
from .introspection import callable_path, create_tool_definition
from .spec import SkillDefinition, SkillSpec, ToolDefinition

F = TypeVar("F", bound=Callable[..., Any])

SKILL_DEFINITION_ATTR = "__toolloom_skill_definition__"
SKILL_SPEC_ATTR = "__toolloom_skill_spec__"


@overload
def skill(func: F, /) -> F: ...


@overload
def skill(
    func: None = None,
    /,
    *,
    name: str | None = None,
    description: str | None = None,
    markdown_path: str | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Callable[[F], F]: ...


def skill(
    func: F | None = None,
    /,
    *,
    name: str | None = None,
    description: str | None = None,
    markdown_path: str | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> F | Callable[[F], F]:
    """Decorate a zero-argument callable as a markdown-backed Toolloom skill."""

    def decorate(target: F) -> F:
        definition = create_skill_definition(
            target,
            name=name,
            description=description,
            markdown_path=markdown_path,
            tags=tags,
            metadata=metadata,
        )
        setattr(target, SKILL_DEFINITION_ATTR, definition)
        setattr(target, SKILL_SPEC_ATTR, definition.spec)
        return target

    if func is not None:
        return decorate(func)
    return decorate


def create_skill_definition(
    func: Callable[..., Any],
    *,
    name: str | None = None,
    description: str | None = None,
    markdown_path: str | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> SkillDefinition:
    """Create a `SkillDefinition` from a zero-argument markdown callable."""

    signature = inspect.signature(func)
    if signature.parameters:
        raise SkillSchemaError(
            f"Skill '{func.__qualname__}' must be a zero-argument callable that returns markdown."
        )

    skill_name = name or func.__name__
    spec = SkillSpec(
        name=skill_name,
        description=description if description is not None else (inspect.getdoc(func) or ""),
        markdown_path=markdown_path,
        tags=list(tags or []),
        callable_path=callable_path(func),
        metadata=dict(metadata or {}),
    )
    return SkillDefinition(spec=spec, func=func)


def get_skill_definition(value: Callable[..., Any] | SkillDefinition) -> SkillDefinition:
    """Return a `SkillDefinition` for a decorated function or definition."""

    if isinstance(value, SkillDefinition):
        return value

    definition = getattr(value, SKILL_DEFINITION_ATTR, None)
    if isinstance(definition, SkillDefinition):
        return definition

    if callable(value):
        return create_skill_definition(value)

    raise SkillSchemaError(f"Object {value!r} is not a Toolloom skill or callable.")


def get_skill_spec(value: Callable[..., Any] | SkillDefinition | SkillSpec) -> SkillSpec:
    """Return a `SkillSpec` without requiring implementation attributes."""

    if isinstance(value, SkillSpec):
        return value
    if isinstance(value, SkillDefinition):
        return value.spec

    spec = getattr(value, SKILL_SPEC_ATTR, None)
    if isinstance(spec, SkillSpec):
        return spec

    return get_skill_definition(value).spec


def skill_to_tool_definition(definition: SkillDefinition) -> ToolDefinition:
    """Expose a markdown skill as a zero-argument framework tool."""

    spec = definition.spec
    metadata = {
        **spec.metadata,
        "toolloom": {
            "kind": "skill",
            "markdown_path": spec.markdown_path,
        },
    }

    wrapper: Callable[..., Any]
    if definition.is_async:

        async def async_read_skill() -> str:
            return await definition.ainvoke()

        wrapper = cast(Callable[..., Any], async_read_skill)
    else:

        def sync_read_skill() -> str:
            return definition.invoke()

        wrapper = sync_read_skill

    wrapper.__name__ = spec.name
    wrapper.__doc__ = spec.description
    return create_tool_definition(
        wrapper,
        name=spec.name,
        description=spec.description,
        tags=spec.tags,
        side_effects=False,
        destructive=False,
        idempotent=True,
        metadata=metadata,
    )


class SkillRegistry:
    """A named collection of markdown-backed Toolloom skill definitions."""

    def __init__(
        self,
        skills: Iterable[Callable[..., Any] | SkillDefinition] | None = None,
    ) -> None:
        self._skills: dict[str, SkillDefinition] = {}
        if skills is not None:
            self.register_many(skills)

    def register(
        self,
        value: Callable[..., Any] | SkillDefinition,
        *,
        replace: bool = False,
    ) -> SkillDefinition:
        """Register one skill and return its definition."""

        definition = get_skill_definition(value)
        name = definition.spec.name
        if name in self._skills and not replace:
            raise SkillRegistrationError(
                f"Skill '{name}' is already registered. Pass replace=True to overwrite it."
            )
        self._skills[name] = definition
        return definition

    def register_many(
        self,
        values: Iterable[Callable[..., Any] | SkillDefinition],
        *,
        replace: bool = False,
    ) -> None:
        """Register multiple skills."""

        for value in values:
            self.register(value, replace=replace)

    def get(self, name: str) -> SkillDefinition:
        """Return a registered skill by name."""

        try:
            return self._skills[name]
        except KeyError as exc:
            raise SkillNotFoundError(name) from exc

    def list(self) -> builtins.list[SkillDefinition]:
        """Return registered skills in insertion order."""

        return list(self._skills.values())

    def names(self) -> builtins.list[str]:
        """Return registered skill names in insertion order."""

        return list(self._skills)

    def as_tool_definitions(self) -> builtins.list[ToolDefinition]:
        """Return skills wrapped as zero-argument documentation tools."""

        return [skill_to_tool_definition(definition) for definition in self.list()]

    def to_fastmcp(self, name: str = "toolloom Skills", **kwargs: Any) -> Any:
        """Export the registry to a FastMCP server."""

        from .adapters.fastmcp import to_fastmcp

        return to_fastmcp(self.as_tool_definitions(), name=name, **kwargs)

    def add_to_fastmcp(self, server: Any) -> Any:
        """Register the skills on an existing FastMCP server and return it."""

        from .adapters.fastmcp import add_to_fastmcp

        return add_to_fastmcp(server, self.as_tool_definitions())

    def to_openai_agents(self) -> builtins.list[Any]:
        """Export the registry to OpenAI Agents SDK tools."""

        from .adapters.openai_agents import to_openai_agents

        return to_openai_agents(self.as_tool_definitions())

    def to_langchain(self) -> builtins.list[Any]:
        """Export the registry to LangChain tools."""

        from .adapters.langchain import to_langchain

        return to_langchain(self.as_tool_definitions())

    def to_langgraph(self) -> builtins.list[Any]:
        """Export the registry to LangGraph-compatible LangChain tools."""

        from .adapters.langgraph import to_langgraph

        return to_langgraph(self.as_tool_definitions())

    def to_langgraph_tool_node(self, **kwargs: Any) -> Any:
        """Export the registry to a LangGraph ToolNode."""

        from .adapters.langgraph import to_langgraph_tool_node

        return to_langgraph_tool_node(self.as_tool_definitions(), **kwargs)
