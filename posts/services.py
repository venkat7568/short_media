"""
Service layer for posts.
Implements business logic for posts and feed.
"""

from typing import List, Optional
from django.db.models import QuerySet
from .models import Post, Comment, Like
from .factories import post_factory
from .repositories import PostRepository, CommentRepository, LikeRepository
from .strategies.ranking import RecencyRankingStrategy, EngagementRankingStrategy
from .strategies.filters import VisibilityFilter, BlockedUsersFilter


class PostService:
    """Service for post operations."""

    def __init__(self):
        self.post_repo = PostRepository()
        self.factory = post_factory

    def create_text_post(self, author, text, visibility='PUBLIC') -> Post:
        """Create a text post."""
        return self.factory.create_text_post(
            author=author,
            text=text,
            visibility=visibility
        )

    def create_image_post(self, author, image, caption='', visibility='PUBLIC') -> Post:
        """Create an image post."""
        return self.factory.create_image_post(
            author=author,
            image=image,
            caption=caption,
            visibility=visibility
        )

    def create_video_post(self, author, video, caption='', duration=0, thumbnail=None, visibility='PUBLIC') -> Post:
        """Create a video post."""
        return self.factory.create_video_post(
            author=author,
            video=video,
            caption=caption,
            duration=duration,
            thumbnail=thumbnail,
            visibility=visibility
        )

    def get_post(self, post_id: int) -> Optional[Post]:
        """Get a post by ID."""
        return self.post_repo.get_by_id(post_id)

    def get_user_posts(self, user, limit: int = None) -> QuerySet:
        """Get posts by a specific user."""
        return self.post_repo.get_by_author(user, limit)

    def delete_post(self, post: Post, user) -> bool:
        """Delete a post (only if user is the author)."""
        if post.author == user:
            self.post_repo.delete(post)
            return True
        return False

    def increment_view(self, post: Post) -> None:
        """Increment view count for a post."""
        post.increment_views()


class FeedService:
    """
    Service for generating personalized feeds.
    Uses Strategy pattern for ranking and filtering.
    """

    def __init__(self, ranking_strategy=None, filters=None):
        self.post_repo = PostRepository()
        self.ranking_strategy = ranking_strategy or RecencyRankingStrategy()
        self.filters = filters or [
            VisibilityFilter(),
            BlockedUsersFilter(),
        ]

    def set_ranking_strategy(self, strategy):
        """Change the ranking strategy at runtime."""
        self.ranking_strategy = strategy

    def add_filter(self, filter_strategy):
        """Add a filter to the feed."""
        self.filters.append(filter_strategy)

    def get_feed(self, user=None, limit: int = 20) -> QuerySet:
        """
        Generate feed for a user.

        Args:
            user: User requesting the feed
            limit: Maximum number of posts

        Returns:
            QuerySet: Filtered and ranked posts
        """
        # Get all posts
        posts = self.post_repo.get_all_posts()

        # Apply all filters
        for filter_strategy in self.filters:
            posts = filter_strategy.execute(posts, user)

        # Apply ranking strategy
        posts = self.ranking_strategy.execute(posts, user)

        # Limit results
        return posts[:limit]

    def get_trending_feed(self, user=None, limit: int = 20) -> QuerySet:
        """Get trending posts."""
        from .strategies.ranking import TrendingRankingStrategy

        self.set_ranking_strategy(TrendingRankingStrategy())
        return self.get_feed(user, limit)

    def search_posts(self, query: str, user=None, limit: int = 20) -> QuerySet:
        """Search posts."""
        posts = self.post_repo.search_posts(query, limit * 2)

        # Apply filters
        for filter_strategy in self.filters:
            posts = filter_strategy.execute(posts, user)

        # Apply ranking
        posts = self.ranking_strategy.execute(posts, user)

        return posts[:limit]


class CommentService:
    """Service for comment operations."""

    def __init__(self):
        self.comment_repo = CommentRepository()

    def add_comment(self, post: Post, author, text: str) -> Comment:
        """Add a comment to a post."""
        return self.comment_repo.create(post, author, text)

    def get_comments(self, post: Post) -> QuerySet:
        """Get comments for a post."""
        return self.comment_repo.get_by_post(post)

    def delete_comment(self, comment: Comment, user) -> bool:
        """Delete a comment (only if user is the author)."""
        if comment.author == user:
            self.comment_repo.delete(comment)
            return True
        return False


class LikeService:
    """Service for like operations."""

    def __init__(self):
        self.like_repo = LikeRepository()

    def toggle_like(self, post: Post, user) -> bool:
        """
        Toggle like on a post.

        Returns:
            bool: True if liked, False if unliked
        """
        if self.like_repo.has_liked(post, user):
            self.like_repo.delete_like(post, user)
            return False
        else:
            self.like_repo.create(post, user)
            return True

    def has_liked(self, post: Post, user) -> bool:
        """Check if user has liked a post."""
        return self.like_repo.has_liked(post, user)

    def get_likes_count(self, post: Post) -> int:
        """Get number of likes for a post."""
        return self.like_repo.get_likes_count(post)
