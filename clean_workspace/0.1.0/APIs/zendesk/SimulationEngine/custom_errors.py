
class OrganizationAlreadyExistsError(Exception):
    """This error is raised when an organization already exists."""
    pass
class UserNotFoundError(Exception):
    """Raised when a user with the given ID does not exist."""
    pass
  
class UserAlreadyExistsError(Exception):
    """Raised when a user with the same ID already exists."""
    pass
  
class OrganizationNotFoundError(Exception):
    pass

class TicketNotFoundError(Exception):
    pass

class TicketAuditNotFoundError(Exception):
    """Raised when an audit with the given ID does not exist."""
    pass

class AttachmentNotFoundError(Exception):
    """Raised when an attachment with the given token or ID does not exist."""
    pass