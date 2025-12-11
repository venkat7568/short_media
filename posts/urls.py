"""URL configuration for posts app."""

from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home_view, name='feed'),
    path('trending/', views.trending_posts_view, name='trending'),
    path('create/', views.create_post_view, name='create_post'),
    path('<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('<int:post_id>/like/', views.like_post_view, name='like_post'),
    path('<int:post_id>/delete/', views.delete_post_view, name='delete_post'),
    path('user/<str:username>/', views.user_posts_view, name='user_posts'),
]
