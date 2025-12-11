"""
Service layer for dating app.

Orchestrates business logic for matching and dating features.
"""

from typing import List, Dict, Optional
from django.db import transaction
from core.exceptions import ValidationException, NotFoundException
from .models import MatchRequest, UserPreferences, Match, MatchStatus
from .repositories import MatchRequestRepository, UserPreferencesRepository, MatchRepository
from .strategies.matching import AttributeMatchingStrategy, BehavioralMatchingStrategy, CompositeMatchingStrategy
from .builders import MatchSearchBuilder


class MatchingService:
    """
    Service for matching users.
    Applies different matching strategies to find compatible users.
    """

    def __init__(self, strategy=None):
        """
        Initialize matching service with a strategy.

        Args:
            strategy: Matching strategy to use (defaults to CompositeMatchingStrategy)
        """
        self.strategy = strategy or CompositeMatchingStrategy()

    def find_matches(self, user, limit: int = 20) -> List[Dict]:
        """
        Find matches for a user using the configured strategy.

        Args:
            user: User to find matches for
            limit: Maximum number of matches to return

        Returns:
            List of match dicts with user and score
        """
        # Build search query with user preferences
        search_builder = MatchSearchBuilder(user)
        search_builder.apply_default_filters()
        search_builder.apply_user_preferences()
        search_builder.exclude_existing_requests()
        search_builder.exclude_existing_matches()

        users_queryset = search_builder.build()

        # Apply matching strategy
        matches = self.strategy.execute(user, users_queryset)

        # Return top matches
        return matches[:limit]

    def set_strategy(self, strategy):
        """
        Change the matching strategy.

        Args:
            strategy: New matching strategy
        """
        self.strategy = strategy


class DatingService:
    """
    Main service for dating features.
    Orchestrates match requests, preferences, and matches.
    """

    def __init__(self):
        """Initialize dating service with repositories and matching service."""
        self.match_request_repo = MatchRequestRepository()
        self.preferences_repo = UserPreferencesRepository()
        self.match_repo = MatchRepository()
        self.matching_service = MatchingService()

    # ===== User Preferences =====

    def get_or_create_preferences(self, user) -> UserPreferences:
        """
        Get or create user dating preferences.

        Args:
            user: User to get preferences for

        Returns:
            UserPreferences instance
        """
        prefs, created = self.preferences_repo.get_or_create(user)
        return prefs

    def update_preferences(self, user, **kwargs) -> UserPreferences:
        """
        Update user dating preferences.

        Args:
            user: User to update preferences for
            **kwargs: Fields to update

        Returns:
            Updated UserPreferences

        Raises:
            ValidationException: If preferences don't exist
        """
        prefs = self.preferences_repo.get_by_user(user)
        if not prefs:
            raise ValidationException("User preferences not found")

        return self.preferences_repo.update(prefs, **kwargs)

    def activate_dating(self, user) -> UserPreferences:
        """
        Activate dating for user (make profile visible).

        Args:
            user: User to activate dating for

        Returns:
            Updated UserPreferences
        """
        return self.update_preferences(user, is_active=True)

    def deactivate_dating(self, user) -> UserPreferences:
        """
        Deactivate dating for user (hide profile).

        Args:
            user: User to deactivate dating for

        Returns:
            Updated UserPreferences
        """
        return self.update_preferences(user, is_active=False)

    # ===== Match Discovery =====

    def discover_matches(self, user, limit: int = 20) -> List[Dict]:
        """
        Discover potential matches for user.
        Shows ALL friends and known people, ranked by compatibility.

        Args:
            user: User to find matches for
            limit: Maximum number of matches

        Returns:
            List of match dicts with user and score
        """
        from django.db.models import Q
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Get all users who are friends (KNOWING) or dating (ACCEPTED)
        known_users_ids = MatchRequest.objects.filter(
            Q(sender=user) | Q(receiver=user),
            status__in=[MatchStatus.KNOWING, MatchStatus.ACCEPTED]
        ).values_list('sender_id', 'receiver_id')

        # Flatten the list and remove the current user's ID
        all_known_ids = set()
        for sender_id, receiver_id in known_users_ids:
            if sender_id != user.id:
                all_known_ids.add(sender_id)
            if receiver_id != user.id:
                all_known_ids.add(receiver_id)

        # Get all these users
        known_users_queryset = User.objects.filter(
            id__in=all_known_ids
        ).select_related('profile', 'dating_preferences')

        # Calculate compatibility scores for all known users
        matches = self.matching_service.strategy.execute(user, known_users_queryset)

        # Return top matches (sorted by score)
        return matches[:limit] if limit else matches

    # ===== Match Requests =====

    @transaction.atomic
    def send_match_request(self, sender, receiver, message: str = '') -> MatchRequest:
        """
        Send a match request to another user.

        Args:
            sender: User sending the request
            receiver: User receiving the request
            message: Optional message with the request

        Returns:
            Created MatchRequest

        Raises:
            ValidationException: If request already exists or users are invalid
        """
        # Validation
        if sender == receiver:
            raise ValidationException("Cannot send match request to yourself")

        if sender.profile.blocked_users.filter(id=receiver.id).exists():
            raise ValidationException("Cannot send match request to blocked user")

        if receiver.profile.blocked_users.filter(id=sender.id).exists():
            raise ValidationException("This user has blocked you")

        # Check if request already exists
        existing_request = self.match_request_repo.get_existing_request(sender, receiver)
        if existing_request:
            if existing_request.is_pending():
                raise ValidationException("Match request already pending")
            elif existing_request.is_accepted():
                raise ValidationException("Already matched with this user")
            elif existing_request.is_blocked():
                raise ValidationException("Cannot send request to this user")

        # Check if already matched
        if self.match_repo.match_exists(sender, receiver):
            raise ValidationException("Already matched with this user")

        # Calculate match score
        matches = self.matching_service.find_matches(sender, limit=100)
        match_score = 0.0
        for match in matches:
            if match['user'] == receiver:
                match_score = match['score']
                break

        # Create request
        return self.match_request_repo.create(
            sender=sender,
            receiver=receiver,
            message=message,
            match_score=match_score
        )

    @transaction.atomic
    def accept_match_request(self, request_id: int, user, response_message: str = '') -> Match:
        """
        Accept a match request.

        Args:
            request_id: ID of the match request
            user: User accepting the request (must be receiver)
            response_message: Optional response message

        Returns:
            Created Match

        Raises:
            NotFoundException: If request doesn't exist
            ValidationException: If user is not the receiver or request is not pending
        """
        match_request = self.match_request_repo.get_by_id(request_id)
        if not match_request:
            raise NotFoundException("Match request not found")

        if match_request.receiver != user:
            raise ValidationException("You are not the receiver of this request")

        if not match_request.is_pending():
            raise ValidationException("Request is not pending")

        # Accept the request
        match_request.accept(response_message)

        # Create the match
        match = self.match_repo.create(
            user1=match_request.sender,
            user2=match_request.receiver,
            match_request=match_request
        )

        return match

    @transaction.atomic
    def reject_match_request(self, request_id: int, user, response_message: str = ''):
        """
        Reject a match request.

        Args:
            request_id: ID of the match request
            user: User rejecting the request (must be receiver)
            response_message: Optional response message

        Raises:
            NotFoundException: If request doesn't exist
            ValidationException: If user is not the receiver or request is not pending
        """
        match_request = self.match_request_repo.get_by_id(request_id)
        if not match_request:
            raise NotFoundException("Match request not found")

        if match_request.receiver != user:
            raise ValidationException("You are not the receiver of this request")

        if not match_request.is_pending():
            raise ValidationException("Request is not pending")

        match_request.reject(response_message)

    @transaction.atomic
    def block_user_from_request(self, request_id: int, user):
        """
        Block the sender of a match request.

        Args:
            request_id: ID of the match request
            user: User blocking the sender (must be receiver)

        Raises:
            NotFoundException: If request doesn't exist
            ValidationException: If user is not the receiver
        """
        match_request = self.match_request_repo.get_by_id(request_id)
        if not match_request:
            raise NotFoundException("Match request not found")

        if match_request.receiver != user:
            raise ValidationException("You are not the receiver of this request")

        # Block the request
        match_request.block()

        # Add sender to blocked users
        user.profile.blocked_users.add(match_request.sender)

    @transaction.atomic
    def cancel_match_request(self, request_id: int, user):
        """
        Cancel a sent match request.

        Args:
            request_id: ID of the match request
            user: User canceling the request (must be sender)

        Raises:
            NotFoundException: If request doesn't exist
            ValidationException: If user is not the sender or request is not pending
        """
        match_request = self.match_request_repo.get_by_id(request_id)
        if not match_request:
            raise NotFoundException("Match request not found")

        if match_request.sender != user:
            raise ValidationException("You are not the sender of this request")

        if not match_request.is_pending():
            raise ValidationException("Can only cancel pending requests")

        self.match_request_repo.delete(match_request)

    def get_pending_received_requests(self, user):
        """Get pending match requests received by user."""
        return self.match_request_repo.get_pending_received_requests(user)

    def get_pending_sent_requests(self, user):
        """Get pending match requests sent by user."""
        return self.match_request_repo.get_pending_sent_requests(user)

    def get_accepted_requests(self, user):
        """Get accepted match requests for user."""
        return self.match_request_repo.get_accepted_requests(user)

    # ===== Matches =====

    def get_user_matches(self, user) -> List[Match]:
        """
        Get all active matches for a user.

        Args:
            user: User to get matches for

        Returns:
            List of Match objects
        """
        return list(self.match_repo.get_user_matches(user, is_active=True))

    @transaction.atomic
    def unmatch(self, match_id: int, user):
        """
        Unmatch with another user.

        Args:
            match_id: ID of the match
            user: User requesting unmatch

        Raises:
            NotFoundException: If match doesn't exist
            ValidationException: If user is not part of the match
        """
        match = self.match_repo.get_by_id(match_id)
        if not match:
            raise NotFoundException("Match not found")

        if match.user1 != user and match.user2 != user:
            raise ValidationException("You are not part of this match")

        match.unmatch()
