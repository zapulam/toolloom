"""Custom exceptions raised by Toolloom."""


class ToolloomError(Exception):
    """Base exception for all Toolloom errors."""


class ToolSchemaError(ToolloomError):
    """Raised when a callable cannot be converted into a supported tool schema."""


class SkillSchemaError(ToolloomError):
    """Raised when a callable cannot be converted into a supported skill."""


class ToolValidationError(ToolloomError):
    """Raised when tool input validation fails."""


class ToolExecutionError(ToolloomError):
    """Raised when a tool callable fails during execution."""


class SkillExecutionError(ToolloomError):
    """Raised when a skill callable fails during execution."""


class ToolTimeoutError(ToolExecutionError):
    """Raised when a tool invocation exceeds its configured timeout."""


class ToolRegistrationError(ToolloomError):
    """Raised when a tool cannot be registered in a registry."""


class SkillRegistrationError(ToolloomError):
    """Raised when a skill cannot be registered in a registry."""


class ToolNotFoundError(ToolloomError, KeyError):
    """Raised when a named tool is not present in a registry."""


class SkillNotFoundError(ToolloomError, KeyError):
    """Raised when a named skill is not present in a registry."""


class ToolAdapterError(ToolloomError):
    """Raised when a framework adapter cannot export a tool."""


class MissingOptionalDependencyError(ToolAdapterError, ImportError):
    """Raised when an optional adapter dependency is not installed."""

    def __init__(self, dependency: str, extra: str) -> None:
        super().__init__(
            f"{dependency} support requires an optional dependency. Install with:\n"
            f'pip install "toolloom[{extra}]"'
        )
        self.dependency = dependency
        self.extra = extra
