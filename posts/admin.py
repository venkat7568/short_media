"""Django admin for posts app."""

from django.contrib import admin
from .models import Post, TextPost, ImagePost, VideoPost, Comment, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post_type', 'visibility', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('post_type', 'visibility', 'created_at')
    search_fields = ('content', 'author__username')
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'comments_count', 'views_count')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'text_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__username')

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
