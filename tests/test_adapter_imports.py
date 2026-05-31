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


@pytest.mark.parametrize(
    ("module_name", "export_method"),
    [
        ("pydantic_ai", "to_pydantic_ai"),
        ("crewai.tools", "to_crewai"),
        ("google.adk.tools", "to_google_adk"),
    ],
)
def test_new_adapters_missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
    export_method: str,
) -> None:
    real_import = importlib.import_module

    def fake_import(name: str, package: str | None = None):
        if name == module_name:
            raise ImportError("missing")
        return real_import(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    with pytest.raises(MissingOptionalDependencyError):
        getattr(ToolRegistry([add]), export_method)()
