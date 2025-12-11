"""
WebSocket routing configuration for Short Media Platform.
Aggregates WebSocket URL patterns from all apps.
"""

from django.urls import path

# Import app-specific routing when apps are created
# from video_calls.routing import websocket_urlpatterns as video_calls_ws
# from notifications.routing import websocket_urlpatterns as notifications_ws

websocket_urlpatterns = [
    # Will be populated when apps with WebSocket consumers are created
    # *video_calls_ws,
    # *notifications_ws,
]
