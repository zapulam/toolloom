"""Small command line helpers for inspecting and linting Toolloom registries."""

from __future__ import annotations

import argparse
import importlib
import json
from typing import Any

from .decorators import get_tool_definition
from .lint import lint_registry, lint_tool
from .registry import ToolRegistry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="toolloom")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect a tool or registry.")
    inspect_parser.add_argument("target", help="Import path like package.module:registry")

    lint_parser = subparsers.add_parser("lint", help="Lint a tool or registry.")
    lint_parser.add_argument("target", help="Import path like package.module:registry")

    args = parser.parse_args(argv)
    target = _load_target(args.target)

    if args.command == "inspect":
        print(json.dumps(_inspect_target(target), indent=2, sort_keys=True))
        return 0

    if args.command == "lint":
        issues = lint_registry(target) if isinstance(target, ToolRegistry) else lint_tool(target)
        print(json.dumps([issue.model_dump() for issue in issues], indent=2, sort_keys=True))
        return 1 if any(issue.severity == "error" for issue in issues) else 0

    return 2


def _load_target(path: str) -> Any:
    module_name, separator, attribute = path.partition(":")
    if not separator or not module_name or not attribute:
        raise SystemExit("Target must use module:attribute syntax.")
    module = importlib.import_module(module_name)
    value: Any = module
    for part in attribute.split("."):
        value = getattr(value, part)
    return value


def _inspect_target(target: Any) -> Any:
    if isinstance(target, ToolRegistry):
        return [definition.spec.model_dump(mode="json") for definition in target.list()]
    return get_tool_definition(target).spec.model_dump(mode="json")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
