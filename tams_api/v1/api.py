"""
Utility methods for the TAMS API
"""

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import get_language

from openedx.core.djangoapps.user_api.preferences import api as preferences_api
from openedx.core.djangoapps.user_api.helpers import intercept_errors

import third_party_auth
from third_party_auth import pipeline

from social.pipeline.social_auth import associate_user
from social.apps.django_app import utils as social_utils

from lang_pref import LANGUAGE_KEY

from student.models import create_comments_service_user, User
from student.views import _do_create_account, AccountValidationError

from ..errors import AccountsAPIInternalError, UserNotFound, UserNotAllowed

def get_user(requesting_user, username):
    """
    Returns the user
    """
    user = None

    if username is None:
        user = requesting_user

    if user is None:
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise UserNotFound

    if user.username != requesting_user.username and not (requesting_user.is_staff or requesting_user.is_superuser):
        raise UserNotAllowed

    # The pre-fetching of groups is done to make auth checks not require an
    # additional DB lookup.
    user = User.objects.prefetch_related('groups').get(id=user.id)

    return user

@intercept_errors(AccountsAPIInternalError, ignore_errors=[ValidationError, AccountValidationError])
def create_user_account(request, params):

    params = dict(params.items())

    params["password"] = pipeline.make_random_password()

    form = AccountCreationForm(
        data=params,
        enforce_username_neq_password=True,
        enforce_password_policy=False,
        tos_required=False
    )

    with transaction.commit_on_success():
        # first, create the account
        (user, profile, registration) = _do_create_account(form)

        uid = params['uid']
        backend_name = 'azuread-oauth2'
        request.social_strategy = social_utils.load_strategy(request)
        redirect_uri = ''
        request.backend = social_utils.load_backend(request.social_strategy, backend_name, redirect_uri)

        # associate the user with azuread
        associate_user(request.backend, uid, user)

        # Perform operations that are non-critical parts of account creation
        preferences_api.set_user_preference(user, LANGUAGE_KEY, get_language())

        create_comments_service_user(user)

        registration.activate()

    return {
        username: user.username,
        email: user.email
    }
