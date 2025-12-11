"""Signals for dating app."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserPreferences


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences(sender, instance, created, **kwargs):
    """
    Auto-create UserPreferences when a User is created.
    """
    if created:
        UserPreferences.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_preferences(sender, instance, **kwargs):
    """
    Save UserPreferences when User is saved.
    """
    if hasattr(instance, 'dating_preferences'):
        instance.dating_preferences.save()
