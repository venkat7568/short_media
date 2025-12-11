"""URL configuration for video calls app."""

from django.urls import path
from . import views

app_name = 'video_calls'

urlpatterns = [
    # Start random call
    path('', views.start_random_call_view, name='start_random'),
    path('start/', views.start_random_call_view, name='start_random'),

    # Call room
    path('room/<str:room_id>/', views.call_room_view, name='call_room'),

    # Call actions
    path('room/<str:room_id>/skip/', views.skip_call_view, name='skip'),
    path('room/<str:room_id>/end/', views.end_call_view, name='end'),

    # API
    path('api/status/<str:room_id>/', views.call_status_view, name='status'),
]
