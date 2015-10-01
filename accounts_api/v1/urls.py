"""
Defines the URL routes for this app.
"""

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(
        r'^accounts$',
        views.AccountsView.as_view(),
        name='accounts_api'
    )
)
