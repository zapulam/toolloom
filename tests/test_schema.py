from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel

from toolloom import get_tool_spec, tool


class Customer(BaseModel):
    name: str
    active: bool = True


class Mode(StrEnum):
    fast = "fast"
    slow = "slow"


def test_parameter_schema_required_defaults_and_descriptions() -> None:
    @tool
    def search(
        query: Annotated[str, "Search query"],
        limit: Annotated[int, "Maximum number of results"] = 10,
    ) -> list[str]:
        """Search records."""
        return [query] * limit

    schema = get_tool_spec(search).parameters_schema

    assert schema["type"] == "object"
    assert schema["properties"]["query"]["type"] == "string"
    assert schema["properties"]["query"]["description"] == "Search query"
    assert schema["properties"]["limit"]["default"] == 10
    assert schema["properties"]["limit"]["description"] == "Maximum number of results"
    assert schema["required"] == ["query"]


def test_schema_supports_structured_types_literals_and_enums() -> None:
    @tool
    def update_customer(
        customer: Customer,
        tags: list[str],
        mode: Literal["safe"],
        speed: Mode,
    ) -> dict:
        """Update a customer record."""
        return {"customer": customer.name, "tags": tags, "mode": mode, "speed": speed}

    spec = get_tool_spec(update_customer)

    assert "$defs" in spec.parameters_schema
    assert spec.parameters_schema["properties"]["tags"]["items"]["type"] == "string"
    assert spec.parameters_schema["properties"]["mode"]["const"] == "safe"
    assert spec.return_schema is not None
    assert spec.return_schema["type"] == "object"
