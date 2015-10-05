"""
Utility methods for the Enrollments API
"""

from django.core.exceptions import ObjectDoesNotExist
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from course_modes.models import CourseMode

from openedx.core.djangoapps.user_api.helpers import intercept_errors

from enrollment import api
from student.models import User

from ..errors import TamsApiInternalError, TamsApiRequestError, UserNotFound, EnrollmentAlreadyExists, InvalidCourseId

@intercept_errors(TamsApiInternalError, ignore_errors=[TamsApiRequestError])
def create_user_enrollment(username, course_id):

    mode = CourseMode.HONOR
    is_active = True

    try:
        course_id = CourseKey.from_string(course_id)
    except InvalidKeyError:
        raise InvalidCourseId

    try:
        user = User.objects.get(username)
    except ObjectDoesNotExist:
        raise UserNotFound

    enrollment = api.get_enrollment(username, unicode(course_id))

    if enrollment:
        raise EnrollmentAlreadyExists

    enrollment = api.add_enrollment(username, unicode(course_id), mode=mode, is_active=is_active)

    return enrollment
