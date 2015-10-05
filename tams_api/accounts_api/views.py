"""
Views for the Accounts API
"""
import logging

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import ugettext as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from openedx.core.lib.api.authentication import (    # pylint: disable=import-error
    SessionAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists

from social.exceptions import AuthAlreadyAssociated

from student.views import AccountValidationError

from ..errors import AccountsApiInternalError, UserNotFound, UserNotAllowed
from .api import get_user, create_user_account

log = logging.getLogger(__name__)

class AccountsView(APIView):

    authentication_classes = (OAuth2AuthenticationAllowInactiveUser, SessionAuthenticationAllowInactiveUser)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, username):
        """
        GET /api/tams_api/accounts/{username}
        """

        try:
            user = get_user(request.user, username)
        except UserNotFound:
            return Response({
                'code': status.HTTP_403_FORBIDDEN,
                'message': 'No such user "{}"'.format(username)
            }, status=status.HTTP_404_NOT_FOUND)
        except UserNotAllowed:
            return Response({
                'code': status.HTTP_403_FORBIDDEN,
                'message': 'Not allowed to retrieve grades for "{}"'.format(username)
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'username': user.username,
            'email': user.email
        })

    def post(self, request):
        """
        POST /api/tams_api/accounts
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
            errorMsg = " and ".join(conflicts)
            return Response({
                'code': status.HTTP_409_CONFLICT,
                'message': "{} already used for another account.".format(errorMsg)
            }, status=status.HTTP_409_CONFLICT)

        data["honor_code"] = True;
        data["terms_of_service"] = True;

        try:

            user = create_user_account(request, data)

        except AccountValidationError as err:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'field': [{"user_message": err.message}]
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as err:
            errors = {
                'field': [{"user_message": error} for error in error_list] for field, error_list in err.message_dict.items()
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        except AuthAlreadyAssociated as err:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': err.message
            }, status=status.HTTP_400_BAD_REQUEST)

        except AccountsApiInternalError as err:
            return Response({
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': err.message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(user)

