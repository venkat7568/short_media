"""
Builder pattern implementation for dating app.

SearchQueryBuilder constructs complex match search queries incrementally.
"""

from datetime import datetime
from django.db.models import Q, QuerySet
from django.contrib.auth import get_user_model
from core.design_patterns.builder import IBuilder


User = get_user_model()


class SearchQueryBuilder(IBuilder):
    """
    Builder for constructing complex user search queries.
    Allows incremental building of filter criteria.
    """

    def __init__(self):
        """Initialize the builder with empty query."""
        self.reset()

    def reset(self):
        """Reset the builder to start a new query."""
        self._queryset = User.objects.select_related('profile', 'dating_preferences').all()
        self._filters = Q()
        return self

    def with_age_range(self, min_age: int, max_age: int):
        """
        Filter users by age range.

        Args:
            min_age: Minimum age
            max_age: Maximum age

        Returns:
            self for chaining
        """
        today = datetime.today()
        max_birth_year = today.year - min_age
        min_birth_year = today.year - max_age - 1

        self._filters &= Q(
            profile__date_of_birth__year__gte=min_birth_year,
            profile__date_of_birth__year__lte=max_birth_year
        )
        return self

    def with_gender(self, gender: str):
        """
        Filter users by gender.

        Args:
            gender: Gender to filter by ('MALE', 'FEMALE', 'OTHER', 'ANY')

        Returns:
            self for chaining
        """
        if gender and gender != 'ANY':
            self._filters &= Q(profile__gender=gender)
        return self

    def with_location(self, location: str):
        """
        Filter users by location (case-insensitive contains).

        Args:
            location: Location to filter by

        Returns:
            self for chaining
        """
        if location:
            self._filters &= Q(profile__location__icontains=location)
        return self

    def with_interests(self, interests: list):
        """
        Filter users by interests (at least one match).

        Args:
            interests: List of interests to match

        Returns:
            self for chaining
        """
        if interests:
            interest_queries = Q()
            for interest in interests:
                interest_queries |= Q(dating_preferences__interests__icontains=interest)
            self._filters &= interest_queries
        return self

    def with_looking_for(self, looking_for: str):
        """
        Filter users by what they're looking for.

        Args:
            looking_for: Relationship type ('FRIENDSHIP', 'DATING', 'RELATIONSHIP', 'ANY')

        Returns:
            self for chaining
        """
        if looking_for and looking_for != 'ANY':
            self._filters &= Q(
                Q(dating_preferences__looking_for=looking_for) |
                Q(dating_preferences__looking_for='ANY')
            )
        return self

    def with_active_preferences(self):
        """
        Filter users with active dating preferences.

        Returns:
            self for chaining
        """
        self._filters &= Q(dating_preferences__is_active=True)
        return self

    def exclude_users(self, user_ids: list):
        """
        Exclude specific users from results.

        Args:
            user_ids: List of user IDs to exclude

        Returns:
            self for chaining
        """
        if user_ids:
            self._queryset = self._queryset.exclude(id__in=user_ids)
        return self

    def exclude_user(self, user):
        """
        Exclude a specific user from results.

        Args:
            user: User to exclude

        Returns:
            self for chaining
        """
        if user:
            self._queryset = self._queryset.exclude(id=user.id)
        return self

    def exclude_blocked_users(self, user):
        """
        Exclude users that the given user has blocked.

        Args:
            user: User whose blocked list to use

        Returns:
            self for chaining
        """
        if user and hasattr(user, 'profile'):
            blocked_ids = user.profile.blocked_users.values_list('id', flat=True)
            if blocked_ids:
                self._queryset = self._queryset.exclude(id__in=blocked_ids)
        return self

    def exclude_users_who_blocked(self, user):
        """
        Exclude users who have blocked the given user.

        Args:
            user: User to check for being blocked

        Returns:
            self for chaining
        """
        if user:
            # Find users who have blocked this user
            blocker_ids = User.objects.filter(
                profile__blocked_users=user
            ).values_list('id', flat=True)
            if blocker_ids:
                self._queryset = self._queryset.exclude(id__in=blocker_ids)
        return self

    def with_verified_users_only(self):
        """
        Filter only verified users.

        Returns:
            self for chaining
        """
        self._filters &= Q(is_verified=True)
        return self

    def order_by_recent_activity(self):
        """
        Order results by recent activity (latest post).

        Returns:
            self for chaining
        """
        self._queryset = self._queryset.order_by('-post__created_at')
        return self

    def limit(self, count: int):
        """
        Limit the number of results.

        Args:
            count: Maximum number of results

        Returns:
            self for chaining
        """
        self._queryset = self._queryset[:count]
        return self

    def build(self) -> QuerySet:
        """
        Build and return the final queryset.

        Returns:
            QuerySet: Constructed queryset with all filters applied
        """
        result = self._queryset.filter(self._filters).distinct()
        # Reset for potential reuse
        return result

    def get_result(self) -> QuerySet:
        """Alias for build() method."""
        return self.build()


class MatchSearchBuilder:
    """
    High-level builder for match searches with user preferences.
    Uses SearchQueryBuilder internally.
    """

    def __init__(self, user):
        """
        Initialize match search for a user.

        Args:
            user: User to find matches for
        """
        self.user = user
        self.builder = SearchQueryBuilder()

    def apply_user_preferences(self):
        """
        Apply the user's dating preferences to the search.

        Returns:
            self for chaining
        """
        if not hasattr(self.user, 'dating_preferences'):
            return self

        prefs = self.user.dating_preferences

        # Apply age range
        if prefs.min_age and prefs.max_age:
            self.builder.with_age_range(prefs.min_age, prefs.max_age)

        # Apply gender preference
        if prefs.preferred_gender:
            self.builder.with_gender(prefs.preferred_gender)

        # Apply location
        if prefs.preferred_location:
            self.builder.with_location(prefs.preferred_location)

        # Apply interests
        interests = prefs.get_interests_list()
        if interests:
            self.builder.with_interests(interests)

        # Apply looking for
        if prefs.looking_for:
            self.builder.with_looking_for(prefs.looking_for)

        return self

    def exclude_existing_requests(self):
        """
        Exclude users who already have pending/accepted requests with this user.

        Returns:
            self for chaining
        """
        from .repositories import MatchRequestRepository

        # Get all users this user has sent requests to
        sent_to_ids = MatchRequestRepository.get_sent_requests(self.user).values_list('receiver_id', flat=True)

        # Get all users who have sent requests to this user
        received_from_ids = MatchRequestRepository.get_received_requests(self.user).values_list('sender_id', flat=True)

        # Combine and exclude
        all_request_ids = list(sent_to_ids) + list(received_from_ids)
        if all_request_ids:
            self.builder.exclude_users(all_request_ids)

        return self

    def exclude_existing_matches(self):
        """
        Exclude users who are already matched with this user.

        Returns:
            self for chaining
        """
        from .repositories import MatchRepository

        matches = MatchRepository.get_user_matches(self.user)
        matched_user_ids = []
        for match in matches:
            other_user = match.get_other_user(self.user)
            matched_user_ids.append(other_user.id)

        if matched_user_ids:
            self.builder.exclude_users(matched_user_ids)

        return self

    def apply_default_filters(self):
        """
        Apply default filters (exclude self, blocked users, inactive preferences).

        Returns:
            self for chaining
        """
        self.builder.exclude_user(self.user)
        self.builder.exclude_blocked_users(self.user)
        self.builder.exclude_users_who_blocked(self.user)
        self.builder.with_active_preferences()
        return self

    def build(self) -> QuerySet:
        """
        Build and return the final queryset.

        Returns:
            QuerySet: Constructed queryset
        """
        return self.builder.build()
