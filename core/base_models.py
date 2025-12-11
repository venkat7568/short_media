"""
Base models for Short Media Platform.
Provides abstract base classes for common model patterns.
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields.
    All models should inherit from this to track creation and modification times.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeletableModel(TimeStampedModel):
    """
    Abstract base model that provides soft delete functionality.
    Instead of deleting records, marks them as deleted.
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark the instance as deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft-deleted instance."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class PublishableModel(TimeStampedModel):
    """
    Abstract base model for content that can be published/unpublished.
    """

    is_published = models.BooleanField(default=True, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def publish(self):
        """Publish the instance."""
        self.is_published = True
        self.published_at = timezone.now()
        self.save()

    def unpublish(self):
        """Unpublish the instance."""
        self.is_published = False
        self.save()
