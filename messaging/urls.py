"""URL configuration for messaging app."""

from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Messaging
    path('inbox/', views.inbox_view, name='inbox'),
    path('conversation/<str:username>/', views.conversation_view, name='conversation'),
    path('send/<str:username>/', views.send_message_view, name='send_message'),

    # Friend requests
    path('requests/', views.friend_requests_view, name='requests'),
    path('friend-request/send/<str:username>/', views.send_friend_request_view, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', views.accept_friend_request_view, name='accept_friend_request'),
    path('friend-request/reject/<int:request_id>/', views.reject_friend_request_view, name='reject_friend_request'),
    path('friend/remove/<int:user_id>/', views.remove_friend_view, name='remove_friend'),
]
