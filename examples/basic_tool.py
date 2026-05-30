from toolloom import get_tool_definition, get_tool_spec, tool


@tool(
    name="search_customers",
    description="Search customers by name, email, or account ID.",
    tags=["crm", "read-only"],
    side_effects=False,
    timeout=10,
)
def search_customers(query: str, limit: int = 10) -> list[dict[str, str]]:
    """Search the CRM for customer records."""
    return [{"name": query, "id": "cus_123"}][:limit]


if __name__ == "__main__":
    print(get_tool_spec(search_customers).model_dump_json(indent=2))
    print(get_tool_definition(search_customers).invoke({"query": "Ada"}))
