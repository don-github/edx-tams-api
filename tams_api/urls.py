"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url, include

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(r'^accounts_api/', include('tams_api.accounts_api.urls', namespace='accounts_api'))
)
