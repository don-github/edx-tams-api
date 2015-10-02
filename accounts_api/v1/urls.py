"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url

from . import views

USERNAME_PATTERN = r'(?P<username>[\w.+-]+)'

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(
        r'^accounts/' + USERNAME_PATTERN + '$',
        views.AccountsView.as_view(),
        name='accounts_api'
    ),
    url(
        r'^accounts$',
        views.AccountsView.as_view(),
        name='accounts_api'
    ),
)
