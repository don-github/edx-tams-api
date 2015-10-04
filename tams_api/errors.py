"""All Error Types pertaining to TAMS API."""


class AccountsApiRequestError(Exception):
    """There was a problem with the request to the Accounts API. """
    pass

class AccountsApiInternalError(Exception):
    """An internal error occurred in the Accounts API. """
    pass

class AccountUserAlreadyExists(AccountsApiRequestError):
    """User with the same username and/or email already exists. """
    pass


class AccountUsernameInvalid(AccountsApiRequestError):
    """The requested username is not in a valid format. """
    pass


class AccountEmailInvalid(AccountsApiRequestError):
    """The requested email is not in a valid format. """
    pass

class UserNotFound(AccountsApiRequestError):
    """The requested user does not exist. """
    pass


class UserNotAllowed(AccountsApiRequestError):
    """The requested user was not allowed to request the grades"""
    pass


