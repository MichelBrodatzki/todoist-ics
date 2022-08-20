class ApiTokenWrongError(Exception):
    """Raised when Todoist returns Unauthorized for current API token."""
    pass

class ApiTokenMissingError(Exception):
    """Raised when no api_token was passed to the TodoistAPI class."""
    pass

class InvalidInputDict(Exception):
    """Raised when an invalid dict was passed to a model."""
    pass
