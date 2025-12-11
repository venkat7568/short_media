"""Dating app models for Short Media Platform."""

from django.db import models
from django.conf import settings
from core.base_models import TimeStampedModel


class MatchStatus(models.TextChoices):
    """Match request status choices."""
    PENDING = 'PENDING', 'Pending'
    KNOWING = 'KNOWING', 'Knowing Each Other'
    ACCEPTED = 'ACCEPTED', 'Dating'
    REJECTED = 'REJECTED', 'Rejected'
    BLOCKED = 'BLOCKED', 'Blocked'


class UserPreferences(TimeStampedModel):
    """
    User dating preferences model.
    Stores user's matching criteria and interests.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dating_preferences'
    )

    # Age preferences
    min_age = models.IntegerField(default=18)
    max_age = models.IntegerField(default=100)

    # Gender preference
    preferred_gender = models.CharField(
        max_length=20,
        choices=[
            ('MALE', 'Male'),
            ('FEMALE', 'Female'),
            ('OTHER', 'Other'),
            ('ANY', 'Any'),
        ],
        default='ANY'
    )

    # Location preferences
    max_distance = models.IntegerField(
        default=50,
        help_text="Maximum distance in kilometers"
    )
    preferred_location = models.CharField(max_length=255, blank=True)

    # Interests (stored as comma-separated values)
    interests = models.TextField(
        blank=True,
        help_text="Comma-separated list of interests"
    )

    # Activity preferences
    looking_for = models.CharField(
        max_length=20,
        choices=[
            ('FRIENDSHIP', 'Friendship'),
            ('DATING', 'Dating'),
            ('RELATIONSHIP', 'Relationship'),
            ('ANY', 'Any'),
        ],
        default='ANY'
    )

    # Visibility
    is_active = models.BooleanField(
        default=True,
        help_text="Whether user wants to appear in matches"
    )

    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"{self.user.username}'s Preferences"

    def get_interests_list(self):
        """Return interests as a list."""
        if not self.interests:
            return []
        return [interest.strip() for interest in self.interests.split(',')]

    def set_interests_list(self, interests_list):
        """Set interests from a list."""
        self.interests = ', '.join(interests_list)


class MatchRequest(TimeStampedModel):
    """
    Match request model.
    Represents a matching request between two users.
    """
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_match_requests'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_match_requests'
    )
    status = models.CharField(
        max_length=10,
        choices=MatchStatus.choices,
        default=MatchStatus.PENDING,
        db_index=True
    )
    message = models.TextField(
        max_length=500,
        blank=True,
        help_text="Optional message with the match request"
    )

    # Matching score (calculated by matching strategies)
    match_score = models.FloatField(default=0.0)

    # Response fields
    response_at = models.DateTimeField(null=True, blank=True)
    response_message = models.TextField(max_length=500, blank=True)

    class Meta:
        db_table = 'match_requests'
        ordering = ['-created_at']
        unique_together = ['sender', 'receiver']
        indexes = [
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.status})"

    def accept(self, message=''):
        """Accept the match request."""
        from django.utils import timezone
        self.status = MatchStatus.ACCEPTED
        self.response_at = timezone.now()
        self.response_message = message
        self.save()

    def reject(self, message=''):
        """Reject the match request."""
        from django.utils import timezone
        self.status = MatchStatus.REJECTED
        self.response_at = timezone.now()
        self.response_message = message
        self.save()

    def block(self):
        """Block the sender."""
        from django.utils import timezone
        self.status = MatchStatus.BLOCKED
        self.response_at = timezone.now()
        self.save()

    def is_pending(self):
        """Check if request is pending."""
        return self.status == MatchStatus.PENDING

    def is_knowing(self):
        """Check if users are knowing each other."""
        return self.status == MatchStatus.KNOWING

    def is_accepted(self):
        """Check if request is accepted (dating)."""
        return self.status == MatchStatus.ACCEPTED

    def is_rejected(self):
        """Check if request is rejected."""
        return self.status == MatchStatus.REJECTED

    def is_blocked(self):
        """Check if sender is blocked."""
        return self.status == MatchStatus.BLOCKED

    def set_knowing(self):
        """Set status to knowing each other."""
        from django.utils import timezone
        self.status = MatchStatus.KNOWING
        self.response_at = timezone.now()
        self.save()

    def breakup(self):
        """Break up the dating relationship (force, no approval needed)."""
        from django.utils import timezone
        if self.status == MatchStatus.ACCEPTED:
            self.status = MatchStatus.REJECTED
            self.response_at = timezone.now()
            self.save()

    def unknow(self):
        """Remove knowing each other status."""
        from django.utils import timezone
        if self.status == MatchStatus.KNOWING:
            self.status = MatchStatus.REJECTED
            self.response_at = timezone.now()
            self.save()


class Match(TimeStampedModel):
    """
    Match model.
    Represents a confirmed match between two users (when both accepted).
    """
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches_as_user1'
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches_as_user2'
    )
    match_request = models.OneToOneField(
        MatchRequest,
        on_delete=models.CASCADE,
        related_name='match'
    )

    # Match statistics
    messages_count = models.IntegerField(default=0)
    last_interaction = models.DateTimeField(auto_now=True)

    # Match status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'matches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user1', 'is_active']),
            models.Index(fields=['user2', 'is_active']),
        ]

    def __str__(self):
        return f"Match: {self.user1.username} ↔ {self.user2.username}"

    def get_other_user(self, user):
        """Get the other user in the match."""
        return self.user2 if self.user1 == user else self.user1

    def unmatch(self):
        """Unmatch users."""
        self.is_active = False
        self.save()
