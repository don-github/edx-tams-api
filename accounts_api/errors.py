"""All Error Types pertaining to Accounts API."""


class AccountsAPIRequestError(Exception):
    """There was a problem with the request to the Accounts API. """
    pass

class AccountsAPIInternalError(Exception):
    """An internal error occurred in the Accounts API. """
    pass

class AccountUserAlreadyExists(AccountsAPIRequestError):
    """User with the same username and/or email already exists. """
    pass


class AccountUsernameInvalid(AccountsAPIRequestError):
    """The requested username is not in a valid format. """
    pass


class AccountEmailInvalid(AccountsAPIRequestError):
    """The requested email is not in a valid format. """
    pass

class UserNotFound(AccountsAPIRequestError):
    """The requested user does not exist. """
    pass


class UserNotAllowed(AccountsAPIRequestError):
    """The requested user was not allowed to request the grades"""
    pass


