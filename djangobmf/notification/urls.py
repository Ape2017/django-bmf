#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from .views import NotificationView
from .views import NotificationUpdate
from .views import NotificationCreate


urlpatterns = patterns(
    '',
    url(
        r'^$', NotificationView.as_view(), name="notification", kwargs={'filter': "unread", 'ct': 0},
    ),
    url(
        r'^(?P<filter>all|active)/$', NotificationView.as_view(), name="notification", kwargs={'ct': 0},
    ),
    url(
        r'^(?P<filter>all|active|unread)/(?P<ct>[0-9]+)/$', NotificationView.as_view(), name="notification",
    ),
    url(
        r'^create/(?P<ct>[0-9]+)/(?P<pk>[0-9]+)/$', NotificationCreate.as_view(), name="notification-create",
    ),
    url(
        r'^update/(?P<pk>[0-9]+)/$', NotificationUpdate.as_view(), name="notification-update",
    ),
)
