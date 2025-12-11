"""Repository layer for dating app."""

from typing import List, Optional
from django.db.models import QuerySet, Q
from django.contrib.auth import get_user_model
from .models import MatchRequest, UserPreferences, Match, MatchStatus


User = get_user_model()


class UserPreferencesRepository:
    """Repository for UserPreferences model."""

    @staticmethod
    def get_by_user(user) -> Optional[UserPreferences]:
        """Get preferences for a user."""
        try:
            return UserPreferences.objects.get(user=user)
        except UserPreferences.DoesNotExist:
            return None

    @staticmethod
    def create(user, **kwargs) -> UserPreferences:
        """Create user preferences."""
        return UserPreferences.objects.create(user=user, **kwargs)

    @staticmethod
    def update(preferences: UserPreferences, **kwargs) -> UserPreferences:
        """Update user preferences."""
        for key, value in kwargs.items():
            setattr(preferences, key, value)
        preferences.save()
        return preferences

    @staticmethod
    def get_or_create(user) -> tuple[UserPreferences, bool]:
        """Get or create preferences for user."""
        return UserPreferences.objects.get_or_create(user=user)


class MatchRequestRepository:
    """Repository for MatchRequest model."""

    @staticmethod
    def create(sender, receiver, message='', match_score=0.0) -> MatchRequest:
        """Create a match request."""
        return MatchRequest.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            match_score=match_score
        )

    @staticmethod
    def get_by_id(request_id: int) -> Optional[MatchRequest]:
        """Get match request by ID."""
        try:
            return MatchRequest.objects.select_related('sender', 'receiver').get(id=request_id)
        except MatchRequest.DoesNotExist:
            return None

    @staticmethod
    def get_sent_requests(user, status: str = None) -> QuerySet:
        """Get requests sent by user."""
        queryset = MatchRequest.objects.filter(sender=user).select_related('receiver', 'receiver__profile')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')

    @staticmethod
    def get_received_requests(user, status: str = None) -> QuerySet:
        """Get requests received by user."""
        queryset = MatchRequest.objects.filter(receiver=user).select_related('sender', 'sender__profile')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')

    @staticmethod
    def get_pending_received_requests(user) -> QuerySet:
        """Get pending requests received by user."""
        return MatchRequestRepository.get_received_requests(user, status=MatchStatus.PENDING)

    @staticmethod
    def get_pending_sent_requests(user) -> QuerySet:
        """Get pending requests sent by user."""
        return MatchRequestRepository.get_sent_requests(user, status=MatchStatus.PENDING)

    @staticmethod
    def get_accepted_requests(user) -> QuerySet:
        """Get accepted requests (both sent and received)."""
        return MatchRequest.objects.filter(
            Q(sender=user) | Q(receiver=user),
            status=MatchStatus.ACCEPTED
        ).select_related('sender', 'receiver').order_by('-created_at')

    @staticmethod
    def request_exists(sender, receiver) -> bool:
        """Check if a request already exists between users."""
        return MatchRequest.objects.filter(
            Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
        ).exists()

    @staticmethod
    def get_existing_request(sender, receiver) -> Optional[MatchRequest]:
        """Get existing request between users (either direction)."""
        try:
            return MatchRequest.objects.get(
                Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
            )
        except MatchRequest.DoesNotExist:
            return None

    @staticmethod
    def delete(match_request: MatchRequest) -> None:
        """Delete a match request."""
        match_request.delete()


class MatchRepository:
    """Repository for Match model."""

    @staticmethod
    def create(user1, user2, match_request: MatchRequest) -> Match:
        """Create a match."""
        return Match.objects.create(
            user1=user1,
            user2=user2,
            match_request=match_request
        )

    @staticmethod
    def get_by_id(match_id: int) -> Optional[Match]:
        """Get match by ID."""
        try:
            return Match.objects.select_related('user1', 'user2', 'match_request').get(id=match_id)
        except Match.DoesNotExist:
            return None

    @staticmethod
    def get_user_matches(user, is_active: bool = True) -> QuerySet:
        """Get all matches for a user."""
        queryset = Match.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).select_related('user1', 'user2', 'user1__profile', 'user2__profile')

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        return queryset.order_by('-created_at')

    @staticmethod
    def match_exists(user1, user2) -> bool:
        """Check if a match exists between users."""
        return Match.objects.filter(
            Q(user1=user1, user2=user2, is_active=True) |
            Q(user1=user2, user2=user1, is_active=True)
        ).exists()

    @staticmethod
    def get_existing_match(user1, user2) -> Optional[Match]:
        """Get existing match between users."""
        try:
            return Match.objects.get(
                Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
            )
        except Match.DoesNotExist:
            return None
