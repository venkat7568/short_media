"""
Post filters implementation.
Implements Strategy pattern for filtering posts.
"""

from django.db.models import Q, QuerySet
from core.design_patterns.strategy import IStrategy
from posts.models import PostVisibility


class VisibilityFilter(IStrategy):
    """
    Filter posts by visibility rules.
    Public posts visible to all, private posts only to author.
    """

    def execute(self, posts: QuerySet, user=None) -> QuerySet:
        """
        Filter posts based on visibility and user.

        Args:
            posts: QuerySet of posts
            user: User viewing the posts

        Returns:
            QuerySet: Filtered posts
        """
        if not user or not user.is_authenticated:
            # Anonymous users see only public posts
            return posts.filter(visibility=PostVisibility.PUBLIC)

        # Authenticated users see:
        # - Public posts
        # - Their own posts (all visibilities)
        # - Friends' FRIENDS visibility posts (TODO: implement friends)
        return posts.filter(
            Q(visibility=PostVisibility.PUBLIC) |
            Q(author=user)
        )


class BlockedUsersFilter(IStrategy):
    """
    Filter out posts from blocked users.
    """

    def execute(self, posts: QuerySet, user=None) -> QuerySet:
        """
        Remove posts from users blocked by the viewing user.

        Args:
            posts: QuerySet of posts
            user: User viewing the posts

        Returns:
            QuerySet: Filtered posts
        """
        if not user or not user.is_authenticated:
            return posts

        # Get blocked user IDs
        try:
            blocked_ids = user.profile.blocked_users.values_list('id', flat=True)
            return posts.exclude(author_id__in=blocked_ids)
        except:
            return posts


class ContentModerationFilter(IStrategy):
    """
    Filter posts based on content moderation.
    Can be enhanced with AI-based moderation.
    """

    def execute(self, posts: QuerySet, user=None) -> QuerySet:
        """
        Filter posts based on moderation rules.

        Args:
            posts: QuerySet of posts
            user: User viewing the posts

        Returns:
            QuerySet: Filtered posts
        """
        # TODO: Implement content moderation
        # - Reported posts
        # - Flagged content
        # - NSFW filtering
        # - Spam detection

        # For now, return all posts
        return posts


class UserPreferenceFilter(IStrategy):
    """
    Filter posts based on user preferences.
    """

    def execute(self, posts: QuerySet, user=None) -> QuerySet:
        """
        Filter posts based on user preferences.

        Args:
            posts: QuerySet of posts
            user: User viewing the posts

        Returns:
            QuerySet: Filtered posts
        """
        if not user or not user.is_authenticated:
            return posts

        # TODO: Implement preference-based filtering
        # - Hide posts with certain keywords
        # - Filter by interests
        # - Language preferences

        return posts
