"""
Post models for Short Media Platform.
Implements Factory pattern for different post types.
"""

from django.db import models
from django.conf import settings
from core.base_models import TimeStampedModel


class PostVisibility(models.TextChoices):
    """Post visibility options."""
    PUBLIC = 'PUBLIC', 'Public'
    FRIENDS = 'FRIENDS', 'Friends Only'
    PRIVATE = 'PRIVATE', 'Private'


class Post(TimeStampedModel):
    """
    Abstract base model for all post types.
    Uses polymorphic pattern - child classes define post_type.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField(max_length=5000, blank=True)
    visibility = models.CharField(
        max_length=10,
        choices=PostVisibility.choices,
        default=PostVisibility.PUBLIC
    )

    # Engagement metrics
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)

    # Post type for factory pattern
    post_type = models.CharField(max_length=20, default='TEXT')

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]

    def __str__(self):
        return f"{self.post_type} Post by {self.author.username}"

    def increment_likes(self):
        """Increment likes count."""
        self.likes_count += 1
        self.save(update_fields=['likes_count'])

    def decrement_likes(self):
        """Decrement likes count."""
        if self.likes_count > 0:
            self.likes_count -= 1
            self.save(update_fields=['likes_count'])

    def increment_comments(self):
        """Increment comments count."""
        self.comments_count += 1
        self.save(update_fields=['comments_count'])

    def increment_views(self):
        """Increment views count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class TextPost(Post):
    """Text-only post."""

    text = models.TextField(max_length=5000)

    class Meta:
        db_table = 'text_posts'

    def save(self, *args, **kwargs):
        self.post_type = 'TEXT'
        self.content = self.text
        super().save(*args, **kwargs)


class ImagePost(Post):
    """Post with image."""

    image = models.ImageField(upload_to='posts/images/')
    caption = models.TextField(max_length=2000, blank=True)

    class Meta:
        db_table = 'image_posts'

    def save(self, *args, **kwargs):
        self.post_type = 'IMAGE'
        self.content = self.caption
        super().save(*args, **kwargs)


class VideoPost(Post):
    """Post with video."""

    video = models.FileField(upload_to='posts/videos/')
    thumbnail = models.ImageField(upload_to='posts/thumbnails/', null=True, blank=True)
    duration = models.IntegerField(default=0, help_text='Duration in seconds')
    caption = models.TextField(max_length=2000, blank=True)

    class Meta:
        db_table = 'video_posts'

    def save(self, *args, **kwargs):
        self.post_type = 'VIDEO'
        self.content = self.caption
        super().save(*args, **kwargs)


class Comment(TimeStampedModel):
    """Comment on a post."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(max_length=1000)

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"


class Like(TimeStampedModel):
    """Like on a post."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    class Meta:
        db_table = 'likes'
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.post}"
