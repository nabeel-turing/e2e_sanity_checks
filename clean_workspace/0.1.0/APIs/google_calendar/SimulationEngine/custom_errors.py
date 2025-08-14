class MissingUpdateDataError(ValueError):
    """
    Raised when attempting to update a component without providing
    at least one modifiable field (e.g., name or description).
    """
    pass

class ProjectNotFoundError(ValueError):
    """Custom exception raised when a project is not found."""
    pass

class EmptyInputError(ValueError):
    """Custom exception raised when a required input field is empty."""
    pass

class InvalidInputError(Exception):
    """
    Raised when an input parameter has an invalid value or format.
    """
    pass

class ResourceNotFoundError(Exception):
    """
    Raised when a requested calendar or event resource is not found.
    """
    pass

class ResourceAlreadyExistsError(Exception):
    """
    Raised when attempting to create or move a resource to a location
    where a resource with the same identifier already exists.
    """
    pass
