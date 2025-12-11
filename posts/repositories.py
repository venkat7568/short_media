"""
Repository layer for posts.
Handles data access and abstracts database operations.
"""

from typing import List, Optional
from django.db.models import QuerySet, Q
from .models import Post, TextPost, ImagePost, VideoPost, Comment, Like


class PostRepository:
    """Repository for Post data access."""

    @staticmethod
    def get_all_posts(limit: int = None) -> QuerySet:
        """Get all posts."""
        queryset = Post.objects.select_related('author').all()
        if limit:
            return queryset[:limit]
        return queryset

    @staticmethod
    def get_recent_posts(limit: int = 50) -> QuerySet:
        """Get recent posts."""
        return Post.objects.select_related('author').order_by('-created_at')[:limit]

    @staticmethod
    def get_by_id(post_id: int) -> Optional[Post]:
        """Get post by ID."""
        try:
            return Post.objects.select_related('author').get(id=post_id)
        except Post.DoesNotExist:
            return None

    @staticmethod
    def get_by_author(author, limit: int = None) -> QuerySet:
        """Get posts by author."""
        queryset = Post.objects.filter(author=author).select_related('author')
        if limit:
            return queryset[:limit]
        return queryset

    @staticmethod
    def delete(post: Post) -> None:
        """Delete a post."""
        post.delete()

    @staticmethod
    def search_posts(query: str, limit: int = 20) -> QuerySet:
        """Search posts by content."""
        return Post.objects.filter(
            Q(content__icontains=query)
        ).select_related('author')[:limit]


class CommentRepository:
    """Repository for Comment data access."""

    @staticmethod
    def create(post: Post, author, text: str) -> Comment:
        """Create a comment."""
        comment = Comment.objects.create(
            post=post,
            author=author,
            text=text
        )
        post.increment_comments()
        return comment

    @staticmethod
    def get_by_post(post: Post) -> QuerySet:
        """Get comments for a post."""
        return Comment.objects.filter(post=post).select_related('author').order_by('created_at')

    @staticmethod
    def delete(comment: Comment) -> None:
        """Delete a comment."""
        comment.delete()


class LikeRepository:
    """Repository for Like data access."""

    @staticmethod
    def create(post: Post, user) -> Like:
        """Create a like."""
        like, created = Like.objects.get_or_create(post=post, user=user)
        if created:
            post.increment_likes()
        return like

    @staticmethod
    def delete_like(post: Post, user) -> bool:
        """Delete a like."""
        try:
            like = Like.objects.get(post=post, user=user)
            like.delete()
            post.decrement_likes()
            return True
        except Like.DoesNotExist:
            return False

    @staticmethod
    def has_liked(post: Post, user) -> bool:
        """Check if user has liked a post."""
        return Like.objects.filter(post=post, user=user).exists()

    @staticmethod
    def get_likes_count(post: Post) -> int:
        """Get number of likes for a post."""
        return Like.objects.filter(post=post).count()
