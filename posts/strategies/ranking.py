"""
Feed ranking strategies implementation.
Implements Strategy pattern for different feed sorting algorithms.
"""

from django.db.models import F, Q, QuerySet
from core.design_patterns.strategy import IStrategy


class RecencyRankingStrategy(IStrategy):
    """
    Rank posts by creation time (newest first).
    Simple and fast strategy.
    """

    def execute(self, posts: QuerySet, user=None) -> QuerySet:
        """
        Sort posts by creation date descending.

        Args:
            posts: QuerySet of posts
            user: Optional user for personalization (not used here)

        Returns:
            QuerySet: Sorted posts
        """
        return posts.order_by('-created_at')


class EngagementRankingStrategy(IStrategy):
    """
    Rank posts by engagement score.
    Score = (likes * 2) + views + comments
    """

    def execute(self, posts: QuerySet, user=None) -> QuerySet:
        """
        Sort posts by engagement score descending.

        Args:
            posts: QuerySet of posts
            user: Optional user for personalization (not used here)

        Returns:
            QuerySet: Sorted posts by engagement
        """
        return posts.annotate(
            engagement_score=F('likes_count') * 2 + F('views_count') + F('comments_count')
        ).order_by('-engagement_score', '-created_at')


class PersonalizedRankingStrategy(IStrategy):
    """
    Personalized ranking based on user preferences and behavior.
    Currently uses engagement but can be enhanced with ML models.
    """

    def execute(self, posts: QuerySet, user=None) -> QuerySet:
        """
        Sort posts using personalized algorithm.

        Args:
            posts: QuerySet of posts
            user: User for personalization

        Returns:
            QuerySet: Sorted posts
        """
        if not user or not user.is_authenticated:
            # Fall back to engagement ranking for anonymous users
            return EngagementRankingStrategy().execute(posts)

        # For now, use engagement ranking
        # TODO: Implement ML-based personalization
        # - User's liked posts
        # - User's commented posts
        # - Similar users' preferences
        # - Content similarity
        return posts.annotate(
            engagement_score=F('likes_count') * 2 + F('views_count') + F('comments_count')
        ).order_by('-engagement_score', '-created_at')


class TrendingRankingStrategy(IStrategy):
    """
    Rank posts by trending score.
    Combines recency with engagement.
    """

    def execute(self, posts: QuerySet, user=None) -> QuerySet:
        """
        Sort posts by trending score.

        Args:
            posts: QuerySet of posts
            user: Optional user

        Returns:
            QuerySet: Sorted posts by trending
        """
        from django.utils import timezone
        from datetime import timedelta

        # Get posts from last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        recent_posts = posts.filter(created_at__gte=week_ago)

        # Sort by engagement within recent posts
        return recent_posts.annotate(
            engagement_score=F('likes_count') * 2 + F('views_count') + F('comments_count')
        ).order_by('-engagement_score', '-created_at')
