from toolloom import get_tool_definition, get_tool_spec, tool


def test_bare_tool_decorator_preserves_callability() -> None:
    @tool
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    assert add(1, 2) == 3
    assert get_tool_spec(add).name == "add"
    assert get_tool_spec(add).description == "Add two numbers."
    assert hasattr(add, "__toolloom_spec__")


def test_configured_tool_decorator_sets_metadata() -> None:
    @tool(
        name="add_numbers",
        description="Add two integers.",
        tags=["math"],
        side_effects=False,
        timeout=5,
    )
    def add(a: int, b: int) -> int:
        return a + b

    spec = get_tool_spec(add)
    assert spec.name == "add_numbers"
    assert spec.description == "Add two integers."
    assert spec.tags == ["math"]
    assert spec.timeout == 5


def test_get_tool_definition_accepts_raw_callable() -> None:
    def greet(name: str) -> str:
        """Greet a person."""
        return f"Hello, {name}"

    definition = get_tool_definition(greet)

    assert definition.spec.name == "greet"
    assert definition.invoke({"name": "Ada"}) == "Hello, Ada"
