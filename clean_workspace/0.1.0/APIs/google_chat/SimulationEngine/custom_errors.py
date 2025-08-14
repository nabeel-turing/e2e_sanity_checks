class InvalidMessageIdFormatError(ValueError):
    """Custom error for invalid messageId format."""
    pass

class InvalidMessageReplyOptionError(ValueError):
    """Custom error for invalid messageReplyOption value."""
    pass

class UserNotMemberError(PermissionError):
    """Custom error raised when a user is not a member of the space."""
    pass

class MissingThreadDataError(ValueError):
    """Custom error raised when thread data is required but not provided."""
    pass

class DuplicateRequestIdError(ValueError):
    """Custom error raised when a duplicate requestId is encountered for the same user."""
    pass

class MissingDisplayNameError(ValueError):
    """Custom error for when displayName is required for a specific spaceType but not provided or is empty."""
    pass

class InvalidPageSizeError(ValueError):
    """Custom error for when pageSize is outside the valid range."""
    pass

class MissingDisplayNameError(ValueError):
    """Custom error raised when displayName is required but missing."""
    pass

# Add new class for validating pageToken
class InvalidPageTokenError(ValueError):
    pass


class InvalidParentFormatError(ValueError):
    """Custom error for invalid parent format."""
    pass

class AdminAccessFilterError(ValueError):
    """Custom error for filter requirements when using admin access."""
    pass

class InvalidSpaceNameFormatError(ValueError):
    """Custom error for invalid space name format."""
    pass

class AdminAccessNotAllowedError(ValueError):
    """Custom error for attempting an action with admin access that is not permitted."""
    pass

class MembershipAlreadyExistsError(ValueError):
    """Custom error for attempting to create a membership that already exists."""
    pass

class InvalidUpdateMaskError(ValueError):
    """Custom error for invalid update mask in patch operations."""
    pass

class MembershipNotFoundError(ValueError):
    """Custom error for membership not found in operations."""
    pass

class NoUpdatableFieldsError(ValueError):
    """Custom error for when no valid updatable fields are provided."""
    pass