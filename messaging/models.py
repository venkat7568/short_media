"""
Models for messaging and friendship system.
"""

from django.db import models
from django.conf import settings
from core.base_models import TimeStampedModel


class Friendship(TimeStampedModel):
    """
    Model for friend relationships.
    Separate from dating relationships.
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('BLOCKED', 'Blocked'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_friend_requests'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    class Meta:
        db_table = 'friendships'
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'
        unique_together = ['sender', 'receiver']
        indexes = [
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['receiver', 'status']),
        ]

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"


class Conversation(TimeStampedModel):
    """
    Model for chat conversations between users.
    """

    participant1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_participant1'
    )
    participant2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_participant2'
    )
    last_message_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        unique_together = ['participant1', 'participant2']
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['participant1', 'last_message_at']),
            models.Index(fields=['participant2', 'last_message_at']),
        ]

    def __str__(self):
        return f"Conversation: {self.participant1.username} <-> {self.participant2.username}"

    def get_other_participant(self, user):
        """Get the other participant in the conversation."""
        if self.participant1 == user:
            return self.participant2
        return self.participant1

    def get_unread_count(self, user):
        """Get count of unread messages for a user."""
        return self.messages.filter(receiver=user, is_read=False).count()


class Message(TimeStampedModel):
    """
    Model for individual messages in conversations.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['receiver', 'is_read']),
        ]

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.text[:50]}"

    def mark_as_read(self):
        """Mark message as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
