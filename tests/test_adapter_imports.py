import importlib

import pytest

from toolloom import ToolRegistry, tool
from toolloom.errors import MissingOptionalDependencyError


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def test_missing_optional_dependency_error_message() -> None:
    error = MissingOptionalDependencyError("LangChain", "langchain")

    assert 'pip install "toolloom[langchain]"' in str(error)


def test_langchain_adapter_missing_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = importlib.import_module

    def fake_import(name: str, package: str | None = None):
        if name == "langchain_core.tools":
            raise ImportError("missing")
        return real_import(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    with pytest.raises(MissingOptionalDependencyError):
        ToolRegistry([add]).to_langchain()
