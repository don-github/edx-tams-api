"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url, include

urlpatterns = patterns(
    '',
    url(r'^accounts_api/', include('tams_api.accounts_api.urls', namespace='accounts_api')),
    url(r'^enrollments_api/', include('tams_api.enrollments_api.urls', namespace='enrollments_api'))
)
