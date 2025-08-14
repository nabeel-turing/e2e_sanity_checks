class MissingPartParameterError(ValueError):
    """Raised when the 'part' parameter is missing or empty."""
    pass

class InvalidMaxResultsError(ValueError):
    """Raised when 'max_results' is provided but is not a positive integer."""

class InvalidPartParameterError(ValueError):
    """Custom error raised when the 'part' parameter is invalid."""
    pass

class MaxResultsOutOfRangeError(ValueError):
    """Custom error for when max_results is outside the allowed range (1-50)."""
    def __init__(self, message="max_results must be between 1 and 50, inclusive."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message