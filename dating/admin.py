"""Django admin for dating app."""

from django.contrib import admin
from .models import UserPreferences, MatchRequest, Match


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'min_age', 'max_age', 'preferred_gender', 'looking_for', 'is_active', 'created_at')
    list_filter = ('preferred_gender', 'looking_for', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'interests')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MatchRequest)
class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'status', 'match_score', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username')
    readonly_fields = ('created_at', 'updated_at', 'response_at')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'messages_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user1__username', 'user2__username')
    readonly_fields = ('created_at', 'updated_at', 'last_interaction')
