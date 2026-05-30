import pytest

from toolloom import SkillRegistry, get_skill_definition, get_skill_spec, skill
from toolloom.errors import SkillExecutionError, SkillRegistrationError, SkillSchemaError


@skill(description="Read the markdown playbook.")
def playbook() -> str:
    return "# Playbook\n\nUse the documented process."


@skill(name="research_notes", description="Read the research notes.")
def notes() -> str:
    return "# Notes"


def test_skill_decorator_preserves_callability() -> None:
    assert playbook() == "# Playbook\n\nUse the documented process."
    assert get_skill_spec(playbook).name == "playbook"
    assert get_skill_spec(playbook).description == "Read the markdown playbook."
    assert hasattr(playbook, "__toolloom_skill_spec__")


def test_configured_skill_metadata() -> None:
    @skill(
        name="support_runbook",
        description="Read the support runbook.",
        markdown_path="skills/support.md",
        tags=["support"],
        metadata={"team": "cx"},
    )
    def support() -> str:
        return "# Support"

    spec = get_skill_spec(support)
    assert spec.name == "support_runbook"
    assert spec.markdown_path == "skills/support.md"
    assert spec.tags == ["support"]
    assert spec.metadata == {"team": "cx"}


def test_skill_rejects_parameters() -> None:
    with pytest.raises(SkillSchemaError):

        @skill
        def invalid(topic: str) -> str:
            return topic


def test_skill_definition_invocation() -> None:
    definition = get_skill_definition(playbook)

    assert definition.invoke().startswith("# Playbook")


@pytest.mark.asyncio
async def test_async_skill_invocation() -> None:
    @skill(description="Read async docs.")
    async def async_docs() -> str:
        return "# Async"

    definition = get_skill_definition(async_docs)

    with pytest.raises(SkillExecutionError, match="ainvoke"):
        definition.invoke()
    assert await definition.ainvoke() == "# Async"


def test_skill_must_return_string() -> None:
    @skill(description="Invalid skill return.")
    def invalid() -> int:
        return 1

    with pytest.raises(SkillExecutionError, match="must return markdown"):
        get_skill_definition(invalid).invoke()


def test_skill_registry_registration_get_list_and_names() -> None:
    registry = SkillRegistry([playbook, notes])

    assert registry.names() == ["playbook", "research_notes"]
    assert registry.get("playbook").invoke().startswith("# Playbook")
    assert registry.list() == [get_skill_definition(playbook), get_skill_definition(notes)]


def test_duplicate_skill_rejected_by_default() -> None:
    registry = SkillRegistry([playbook])

    with pytest.raises(SkillRegistrationError):
        registry.register(playbook)


def test_skill_registry_replacement() -> None:
    @skill(name="playbook")
    def replacement() -> str:
        """Read replacement docs."""
        return "# Replacement"

    registry = SkillRegistry([playbook])
    registry.register(replacement, replace=True)

    assert registry.get("playbook").invoke() == "# Replacement"


def test_skill_exports_as_zero_argument_tool_definition() -> None:
    definition = SkillRegistry([playbook]).as_tool_definitions()[0]

    assert definition.spec.name == "playbook"
    assert definition.invoke({}).startswith("# Playbook")
    assert definition.spec.metadata["toolloom"]["kind"] == "skill"
