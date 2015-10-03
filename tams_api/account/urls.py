"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url

from . import views

USERNAME_PATTERN = r'(?P<username>[\w.+-]+)'

urlpatterns = patterns(  # pylint: disable=invalid-name
    'views',
    url(
        r'^accounts/' + USERNAME_PATTERN + '$',
        AccountsView.as_view(),
        name='accounts_detail'
    ),
    url(
        r'^accounts$',
        AccountsView.as_view(),
        name='accounts_api'
    )
)
