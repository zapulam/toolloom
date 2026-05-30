"""Schema generation helpers for Python callables."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from types import NoneType
from typing import Annotated, Any, get_args, get_origin, get_type_hints

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, create_model
from pydantic.fields import FieldInfo

from .errors import ToolSchemaError


class EmptyInputModel(BaseModel):
    """Input model used for tools without parameters."""

    model_config = ConfigDict(extra="forbid")


def build_input_model(func: Callable[..., Any], *, name: str | None = None) -> type[BaseModel]:
    """Build a Pydantic model that represents a callable's keyword arguments."""

    signature = inspect.signature(func)
    hints = get_type_hints(func, include_extras=True)
    fields: dict[str, Any] = {}

    for parameter in signature.parameters.values():
        if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
            raise ToolSchemaError(
                f"Parameter '{parameter.name}' on {func.__qualname__} is positional-only; "
                "Toolloom tools must be callable with keyword arguments."
            )
        if parameter.kind in {
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        }:
            raise ToolSchemaError(
                f"Parameter '{parameter.name}' on {func.__qualname__} uses *args or **kwargs; "
                "Toolloom requires explicit parameters."
            )

        annotation = hints.get(parameter.name, Any)
        annotation, description = unwrap_annotated_description(annotation)
        default = parameter.default if parameter.default is not inspect.Parameter.empty else ...
        fields[parameter.name] = (annotation, Field(default, description=description))

    if not fields:
        return EmptyInputModel

    model_name = name or f"{func.__name__.title().replace('_', '')}Input"
    return create_model(
        model_name,
        __config__=ConfigDict(extra="forbid"),
        **fields,
    )


def parameter_schema(input_model: type[BaseModel]) -> dict[str, Any]:
    """Return the JSON schema for a generated input model."""

    schema = input_model.model_json_schema()
    schema.setdefault("type", "object")
    schema.setdefault("properties", {})
    return schema


def return_schema(func: Callable[..., Any]) -> dict[str, Any] | None:
    """Return JSON schema for a callable's return annotation when present."""

    hints = get_type_hints(func, include_extras=True)
    annotation = hints.get("return")
    if annotation is None or annotation is inspect.Signature.empty:
        return None

    annotation, _ = unwrap_annotated_description(annotation)
    if annotation is None or annotation is NoneType:
        return {"type": "null"}

    try:
        return TypeAdapter(annotation).json_schema()
    except Exception as exc:  # pragma: no cover - pydantic's failures vary by type
        raise ToolSchemaError(
            f"Return annotation for {func.__qualname__} is not supported: {annotation!r}"
        ) from exc


def unwrap_annotated_description(annotation: Any) -> tuple[Any, str | None]:
    """Extract a plain type and the first description from typing.Annotated metadata."""

    if get_origin(annotation) is not Annotated:
        return annotation, None

    args = get_args(annotation)
    base = args[0]
    description: str | None = None
    for item in args[1:]:
        if isinstance(item, str) and description is None:
            description = item
        elif isinstance(item, FieldInfo) and item.description and description is None:
            description = item.description
    return base, description
