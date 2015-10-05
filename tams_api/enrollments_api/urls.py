"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(
        r'^enrollments$',
        views.EnrollmentsView.as_view(),
        name='enrollments_api'
    )
)
