"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url, include

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(
        r'^v1/',
        include('accounts_api.v1.urls', namespace='v1')
    )
)
