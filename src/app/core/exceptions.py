"""Application-specific exceptions (handlers in `app.core.exception_handlers`)."""


class ReferenceConflictError(Exception):
    """Raised when a sub-bill reference collides with an existing row (DB unique)."""

    def __init__(
        self, message: str = "A sub-bill with this reference already exists."
    ) -> None:
        self.message = message
        super().__init__(message)
