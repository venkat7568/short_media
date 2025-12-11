"""
Django admin configuration for users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile, OTPVerification

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""

    list_display = ('email', 'username', 'is_verified', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_verified', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'last_seen')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""

    list_display = ('user', 'location', 'gender', 'posts_count', 'followers_count', 'following_count', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('user__email', 'user__username', 'location', 'bio')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Profile Information', {
            'fields': ('bio', 'profile_picture', 'date_of_birth', 'gender', 'location', 'interests'),
        }),
        ('Statistics', {
            'fields': ('posts_count', 'followers_count', 'following_count'),
        }),
        ('Privacy', {
            'fields': ('blocked_users',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    """Admin configuration for OTPVerification model."""

    list_display = ('user', 'code', 'purpose', 'is_used', 'expires_at', 'created_at')
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('user__email', 'user__username', 'code')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('OTP Details', {
            'fields': ('code', 'purpose', 'is_used', 'expires_at'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
