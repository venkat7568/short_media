"""Video calls models for Short Media Platform."""

from django.db import models
from django.conf import settings
from core.base_models import TimeStampedModel


class CallStatus(models.TextChoices):
    """Call status choices."""
    WAITING = 'WAITING', 'Waiting'
    RINGING = 'RINGING', 'Ringing'
    ACTIVE = 'ACTIVE', 'Active'
    ENDED = 'ENDED', 'Ended'
    MISSED = 'MISSED', 'Missed'
    REJECTED = 'REJECTED', 'Rejected'


class VideoCallSession(TimeStampedModel):
    """
    Video call session model.
    Supports both direct calls and random Omegle-style matching.
    """
    caller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calls_made'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calls_received',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=CallStatus.choices,
        default=CallStatus.WAITING,
        db_index=True
    )

    # Call type
    is_random = models.BooleanField(
        default=False,
        help_text="Whether this is a random Omegle-style call"
    )

    # Call timing
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0, help_text="Duration in seconds")

    # WebRTC connection data
    room_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'video_calls'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_random']),
            models.Index(fields=['caller', 'status']),
            models.Index(fields=['receiver', 'status']),
        ]

    def __str__(self):
        if self.receiver:
            return f"Call: {self.caller.username} → {self.receiver.username} ({self.status})"
        return f"Random Call: {self.caller.username} ({self.status})"
