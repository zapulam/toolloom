"""Shared adapter helpers."""

from __future__ import annotations

import importlib
from types import ModuleType

from toolloom.errors import MissingOptionalDependencyError


def import_optional(module_name: str, *, dependency: str, extra: str) -> ModuleType:
    """Import an optional adapter dependency with a Toolloom-specific error."""

    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        raise MissingOptionalDependencyError(dependency, extra) from exc
