"""All Error Types pertaining to TAMS API."""


class TamsApiRequestError(Exception):
    """There was a problem with the request to the TAMS API. """
    pass

class TamsApiInternalError(Exception):
    """An internal error occurred in the TAMS API. """
    pass

class AccountUserAlreadyExists(TamsApiRequestError):
    """User with the same username and/or email already exists. """
    pass


class AccountUsernameInvalid(TamsApiRequestError):
    """The requested username is not in a valid format. """
    pass


class AccountEmailInvalid(TamsApiRequestError):
    """The requested email is not in a valid format. """
    pass

class UserNotFound(TamsApiRequestError):
    """The requested user does not exist. """
    pass


class UserNotAllowed(TamsApiRequestError):
    """The requested user was not allowed to request the grades"""
    pass


