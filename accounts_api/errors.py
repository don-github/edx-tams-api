"""
Errors thrown by the accounts api.
"""


class AccountsAPIRequestError(Exception):
    """There was a problem with the request to the Accounts API. """
    pass


class UserNotFound(AccountsAPIRequestError):
    """The requested user does not exist. """
    pass


class UserNotAllowed(AccountsAPIRequestError):
    """The requested user was not allowed to request the accounts"""
    pass
