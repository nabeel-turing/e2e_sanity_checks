class InvalidAttributeError(ValueError):
    """Custom error for invalid attribute names in the 'attributes' parameter."""
    pass


class InvalidPaginationParameterError(ValueError):
    """Custom error for invalid 'startIndex' or 'count' parameter values."""
    pass


class InvalidSortByValueError(ValueError):
    """Custom error for invalid 'sortBy' parameter values."""
    pass


class InvalidSortOrderValueError(ValueError):
    """Custom error for invalid 'sortOrder' parameter values."""
    pass
class ProjectIDMismatchError(ValueError):
    """Custom error raised when the ID in the path does not match the ID in the project_data payload."""
    pass


class ResourceConflictError(ValueError):
    """Custom error for resource conflicts (e.g., duplicate userName on SCIM User creation)."""
    pass


class UserValidationError(ValueError):
    """Custom error for user data validation failures."""
    pass


class UserCreationError(ValueError):
    """Custom error for user creation failures."""
    pass


class UserPatchValidationError(ValueError):
    """Custom error for user PATCH data validation failures."""
    pass


class UserPatchForbiddenError(ValueError):
    """Custom error for forbidden PATCH operations (e.g., self-deactivation, userName domain mismatch)."""
    pass


class UserPatchOperationError(ValueError):
    """Custom error for PATCH operation failures."""
    pass


class UserUpdateValidationError(ValueError):
    """Custom error for user PUT data validation failures."""
    pass


class UserUpdateForbiddenError(ValueError):
    """Custom error for forbidden PUT operations (e.g., self-deactivation, userName domain mismatch)."""
    pass


class UserUpdateConflictError(ValueError):
    """Custom error for PUT operation conflicts (e.g., duplicate userName)."""
    pass


class UserUpdateOperationError(ValueError):
    """Custom error for PUT operation failures."""
    pass


class UserDeleteForbiddenError(ValueError):
    """Custom error for forbidden DELETE operations (e.g., self-deactivation)."""
    pass


class UserDeleteOperationError(ValueError):
    """Custom error for DELETE operation failures."""
    pass