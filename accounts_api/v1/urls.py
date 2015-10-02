"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url

from . import views

USERNAME_PATTERN = '(?P<username>[\w.@+-]+)'

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(r'^accounts/{username}$'.format(username=USERNAME_PATTERN), views.AccountsView.as_view(), name='accounts_api'),
    url(r'^accounts$', views.AccountsView.as_view(), name='accounts_api'),
)
