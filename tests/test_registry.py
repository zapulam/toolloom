import pytest

from toolloom import ToolRegistry, get_tool_definition, tool
from toolloom.errors import ToolRegistrationError


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool(name="search")
def find(query: str) -> list[str]:
    """Search records."""
    return [query]


def test_registry_registration_get_list_and_names() -> None:
    registry = ToolRegistry()
    registry.register(add)
    registry.register(find)

    assert registry.names() == ["add", "search"]
    assert registry.get("add").invoke({"a": 1, "b": 2}) == 3
    assert registry.list() == [get_tool_definition(add), get_tool_definition(find)]


def test_duplicate_tool_rejected_by_default() -> None:
    registry = ToolRegistry([add])

    with pytest.raises(ToolRegistrationError):
        registry.register(add)


def test_registry_replacement() -> None:
    @tool(name="add")
    def replacement(a: int, b: int) -> int:
        """Subtract numbers."""
        return a - b

    registry = ToolRegistry([add])
    registry.register(replacement, replace=True)

    assert registry.get("add").invoke({"a": 5, "b": 2}) == 3
