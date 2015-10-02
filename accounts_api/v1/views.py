"""
Views for the Accounts API
"""
import logging

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import get_language

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from social.pipeline.social_auth import associate_user
from social.apps.django_app import utils as social_utils

from lang_pref import LANGUAGE_KEY

import third_party_auth
from third_party_auth import pipeline

from openedx.core.djangoapps.user_api.preferences import api as preferences_api
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists
from openedx.core.djangoapps.user_api.helpers import intercept_errors
from openedx.core.lib.api.authentication import (
    SessionAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)

from student.views import _do_create_account, AccountValidationError
from student.models import create_comments_service_user

from ..errors import AccountsAPIInternalError

log = logging.getLogger(__name__)

class AccountsView(APIView):

    authentication_classes = (
        OAuth2AuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser
    )
    permission_classes = (permissions.IsAuthenticated)

    def post(self, request):
        """
        POST /api/accounts_api/v1/accounts
            email, username, name, uid
        """

        # Only superusers can create an account
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = request.POST.copy()

        email = data.get('email')
        username = data.get('username')

        # Handle duplicate email/username
        conflicts = check_account_exists(email=email, username=username)

        if conflicts:
            conflict_messages = {
                # Translators: This message is shown to users who attempt to create a new
                # account using an email address associated with an existing account.
                "email": _(
                    u"It looks like {email_address} belongs to an existing account. Try again with a different email address."
                ).format(email_address=email),
                # Translators: This message is shown to users who attempt to create a new
                # account using a username associated with an existing account.
                "username": _(
                    u"It looks like {username} belongs to an existing account. Try again with a different username."
                ).format(username=username),
            }
            errors = {
                field: [{"user_message": conflict_messages[field]}]
                for field in conflicts
            }
            return Response(errors, status=status.HTTP_409_CONFLICT)

        data["honor_code"] = True;
        data["terms_of_service"] = True;

        try:

            user = _create_user_account(request, data)

        except AccountValidationError as err:
            errors = {
                field: [{"user_message": err.message}]
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as err:
            # Should only get non-field errors from this function
            assert NON_FIELD_ERRORS not in err.message_dict
            # Only return first error for each field
            errors = {
                field: [{"user_message": error} for error in error_list]
                for field, error_list in err.message_dict.items()
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        except AccountsAPIInternalError as err:

            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(user)

    @intercept_errors(AccountsAPIInternalError, ignore_errors=[ValidationError, AccountValidationError])
    def _create_user_account(request, params):

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
