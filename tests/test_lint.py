from toolloom import ToolRegistry, lint_registry, lint_tool, tool


def test_lint_reports_quality_issues() -> None:
    @tool(name="run", destructive=True, side_effects=False)
    def bad(x, payload: dict):
        return payload

    issues = lint_tool(bad)
    codes = {issue.code for issue in issues}

    assert "description-too-short" in codes or "missing-description" in codes
    assert "generic-tool-name" in codes
    assert "missing-parameter-type" in codes
    assert "vague-parameter-name" in codes
    assert "missing-return-type" in codes
    assert "destructive-without-side-effects" in codes


def test_lint_registry_aggregates_issues() -> None:
    @tool(description="This tool writes a record to the backing service.", side_effects=True)
    def create_record(name: str) -> str:
        return name

    registry = ToolRegistry([create_record])

    assert any(
        issue.code == "side-effects-idempotency-unknown"
        for issue in lint_registry(registry)
    )


def test_vague_parameter_with_description_is_allowed() -> None:
    from typing import Annotated

    @tool(description="Validate a structured payload before storing it.")
    def validate(payload: Annotated[dict, "Customer update payload"]) -> dict:
        return payload

    assert "vague-parameter-name" not in {issue.code for issue in lint_tool(validate)}
