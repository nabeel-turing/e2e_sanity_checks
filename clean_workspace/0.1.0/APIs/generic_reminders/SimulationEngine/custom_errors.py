class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


class ReminderNotFoundError(ValueError):
    """Raised when a requested reminder cannot be found."""

    pass


class InvalidTimeError(ValueError):
    """Raised when trying to set a reminder for a past time."""

    pass


class OperationNotFoundError(ValueError):
    """Raised when trying to undo an operation that doesn't exist."""

    pass
