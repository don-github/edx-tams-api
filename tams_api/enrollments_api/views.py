"""
Views for the Enrollments API
"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from openedx.core.lib.api.authentication import (
    SessionAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)

from .api import create_user_enrollment

from ..errors import TamsApiInternalError, UserNotFound, EnrollmentAlreadyExists, InvalidCourseId

log = logging.getLogger(__name__)

class EnrollmentsView(APIView):

    authentication_classes = (OAuth2AuthenticationAllowInactiveUser, SessionAuthenticationAllowInactiveUser)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """
        POST /api/tams_api/enrollments_api/enrollments
            username, course_id
        """

        # Only superusers can create an account
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        username = request.POST.get('username')
        course_id = request.POST.get('course_id')

        if not username:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': "username must be specified to create a new enrollment."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not course_id:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': "Course ID must be specified to create a new enrollment."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = create_user_enrollment(username, course_id)

        except InvalidCourseId:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': "Course ID {} is not valid.".format(course_id)
            }, status=status.HTTP_400_BAD_REQUEST)

        except UserNotFound:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': "Username {} is not found.".format(username)
            }, status=status.HTTP_400_BAD_REQUEST)

        except EnrollmentAlreadyExists:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': "User {} has already been enrolled in this course {}.".format(username, course_id)
            }, status=status.HTTP_400_BAD_REQUEST)

        except TamsApiInternalError as err:
            return Response({
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': err.message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response)