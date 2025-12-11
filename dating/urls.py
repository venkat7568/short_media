"""URL configuration for dating app."""

from django.urls import path
from . import views

app_name = 'dating'

urlpatterns = [
    # Discovery
    path('', views.discover_matches_view, name='discover'),
    path('discover/', views.discover_matches_view, name='discover'),

    # Match Requests
    path('requests/', views.match_requests_view, name='requests'),
    path('request/send/<int:user_id>/', views.send_match_request_view, name='send_request'),
    path('request/<int:request_id>/accept/', views.accept_match_request_view, name='accept_request'),
    path('request/<int:request_id>/reject/', views.reject_match_request_view, name='reject_request'),
    path('request/<int:request_id>/block/', views.block_user_from_request_view, name='block_user'),
    path('request/<int:request_id>/cancel/', views.cancel_match_request_view, name='cancel_request'),

    # Matches
    path('matches/', views.my_matches_view, name='matches'),
    path('match/<int:match_id>/unmatch/', views.unmatch_view, name='unmatch'),

    # Preferences
    path('preferences/', views.preferences_view, name='preferences'),

    # Know Each Other & Dating Flow
    path('knowing/send/<int:user_id>/', views.send_knowing_request_view, name='send_knowing_request'),
    path('knowing/accept/<int:request_id>/', views.accept_knowing_request_view, name='accept_knowing_request'),
    path('knowing/unknow/<int:user_id>/', views.unknow_view, name='unknow'),
    path('dating/send/<int:user_id>/', views.send_dating_request_view, name='send_dating_request'),
    path('dating/breakup/<int:user_id>/', views.breakup_view, name='breakup'),
]
