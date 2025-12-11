"""
URL configuration for Short Media Platform project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home_view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home
    path('', home_view, name='home'),

    # Users app
    path('users/', include('users.urls')),

    # Posts app
    path('posts/', include('posts.urls')),

    # Dating app
    path('dating/', include('dating.urls')),

    # Video calls app
    path('calls/', include('video_calls.urls')),

    # Messaging app
    path('messages/', include('messaging.urls')),

    # Will be added in later phases:
    # path('notifications/', include('notifications.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else '')
