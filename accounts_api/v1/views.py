"""
Views for the Accounts API
"""

from user_api.accounts.api import check_account_exists

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from microsite_configuration import microsite

from util.password_policy_validators import (
    validate_password_length, validate_password_complexity,
    validate_password_dictionary
)

import third_party_auth
from third_party_auth import pipeline, provider

from student.views import _do_create_account, AccountValidationError

from openedx.core.lib.api.authentication import (    # pylint: disable=import-error
    OAuth2AuthenticationAllowInactiveUser,
)

from ..errors import UserNotFound, UserNotAllowed
from .api import get_user

from social.pipeline.social_auth import associate_user

class AccountsView(APIView):

    FIELDS = ["email", "name", "username", "password", "honor_code"]

    authentication_classes = (
        OAuth2AuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id):
        """
        GET /api/grades_api/v1/grades/{course_id}?username={username}
        """

        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        username = request.QUERY_PARAMS.get('username')

        try:
            user = get_user(request.user, username)
        except UserNotFound:
            return Response({
                'error': 'No such user "{}"'.format(username)
            }, status=status.HTTP_404_NOT_FOUND)
        except UserNotAllowed:
            return Response({
                'error': 'Not allowed to retrieve grades for "{}"'.format(username)
            }, status=status.HTTP_403_FORBIDDEN)

        course = get_course_with_access(user, 'load', course_key, depth=None)
        grade_summary = grades.grade(user, request, course)

        return Response({
            'username': user.username,
            'course_id': course_id,
            'percent': grade_summary.get('percent')
        })

    def post(self, request):
        """
        POST /api/accounts_api/v1/accounts
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

        if data.get("honor_code") and "terms_of_service" not in data:
            data["terms_of_service"] = data["honor_code"]

        try:
            user = _create_user_account(request, data)
        except ValidationError as err:
            # Should only get non-field errors from this function
            assert NON_FIELD_ERRORS not in err.message_dict
            # Only return first error for each field
            errors = {
                field: [{"user_message": error} for error in error_list]
                for field, error_list in err.message_dict.items()
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            username: user.username,
            email: user.email
        })

    def _create_user_account(request, params):

        params = dict(params.items())

        params["password"] = pipeline.make_random_password()

        extra_fields = microsite.get_value(
            'REGISTRATION_EXTRA_FIELDS',
            getattr(settings, 'REGISTRATION_EXTRA_FIELDS', {})
        )

        extended_profile_fields = microsite.get_value('extended_profile_fields', [])

        form = AccountCreationForm(
            data=params,
            extra_fields=extra_fields,
            extended_profile_fields=extended_profile_fields,
            enforce_username_neq_password=True,
            enforce_password_policy=False,
            tos_required=False
        )

        with transaction.commit_on_success():
            # first, create the account
            (user, profile, registration) = _do_create_account(form)

            uid = params['uid']

            # associate the user with azuread
            azure_user = associate_user(request.backend, uid, user)

        # Perform operations that are non-critical parts of account creation
        preferences_api.set_user_preference(user, LANGUAGE_KEY, get_language())

        if settings.FEATURES.get('ENABLE_DISCUSSION_EMAIL_DIGEST'):
            try:
                enable_notifications(user)
            except Exception:
                log.exception("Enable discussion notifications failed for user {id}.".format(id=user.id))

        dog_stats_api.increment("common.student.account_created")

        # Track the user's registration
        if settings.FEATURES.get('SEGMENT_IO_LMS') and hasattr(settings, 'SEGMENT_IO_LMS_KEY'):
            tracking_context = tracker.get_tracker().resolve_context()
            analytics.identify(user.id, {
                'email': user.email,
                'username': user.username,
            })

            analytics.track(
                user.id,
                "edx.bi.user.account.registered",
                {
                    'category': 'conversion',
                    'label': params.get('course_id'),
                    'provider': third_party_provider.name if third_party_provider else None
                },
                context={
                    'Google Analytics': {
                        'clientId': tracking_context.get('client_id')
                    }
                }
            )

        create_comments_service_user(user)

        registration.activate()
