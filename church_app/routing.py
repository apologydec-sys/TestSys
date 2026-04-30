"""
Django Channels routing configuration for WebSocket endpoints
"""

from django.urls import re_path
from .consumers import MemberConsumer, AttendanceConsumer, AnnouncementConsumer

websocket_urlpatterns = [
    re_path(r'ws/members/$', MemberConsumer.as_asgi()),
    re_path(r'ws/attendance/$', AttendanceConsumer.as_asgi()),
    re_path(r'ws/announcements/$', AnnouncementConsumer.as_asgi()),
]
