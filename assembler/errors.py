"""Domain-specific exception hierarchy for the assembler.

Provides meaningful exception types to distinguish between:
- User-facing syntax errors (AsmSyntaxError)
- Semantic/validation errors (AsmSemanticError)
- Programming logic errors (AsmInternalError)
"""


class AsmError(Exception):
    """Base exception for all assembler domain errors."""

    def __init__(self, message: str, line: int | None = None):
        self.message = message
        self.line = line
        if line is not None:
            super().__init__(f"Line {line}: {message}")
        else:
            super().__init__(message)


class AsmSyntaxError(AsmError):
    """Raised when assembly syntax is invalid (wrong number of arguments, wrong argument types, etc.)."""

    pass


class AsmSemanticError(AsmError):
    """Raised when assembly is syntactically correct but semantically invalid (undefined labels, invalid values, etc.)."""

    pass


class AsmInternalError(AsmError):
    """Raised for internal assembler errors that indicate programmer bugs, not user errors."""

    pass
