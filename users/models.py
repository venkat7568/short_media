"""
User models for Short Media Platform.
Implements custom user model, profiles, and OTP verification.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from datetime import date
from core.base_models import TimeStampedModel
from core.utils import generate_otp, is_otp_expired


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Uses email as the primary identifier instead of username.
    """

    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    # Make email the primary login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def is_blocked_by(self, user):
        """Check if this user is blocked by another user."""
        return self.profile.blocked_users.filter(id=user.id).exists()

    def block_user(self, user_to_block):
        """Block another user."""
        self.profile.blocked_users.add(user_to_block)

    def unblock_user(self, user_to_unblock):
        """Unblock another user."""
        self.profile.blocked_users.remove(user_to_unblock)


class UserProfile(TimeStampedModel):
    """
    Extended user profile with additional information.
    One-to-one relationship with User model.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True, default='')
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True,
        default=''
    )
    location = models.CharField(max_length=100, blank=True, default='')
    interests = models.JSONField(default=list, blank=True)
    relationship_status = models.CharField(
        max_length=20,
        choices=[
            ('single', 'Single'),
            ('in_relationship', 'In a Relationship'),
            ('engaged', 'Engaged'),
            ('married', 'Married'),
            ('complicated', 'It\'s Complicated'),
            ('open_relationship', 'In an Open Relationship'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True,
        default=''
    )

    # Privacy settings
    blocked_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='blocked_by',
        blank=True
    )
    show_in_dating_search = models.BooleanField(default=True)  # Appear in dating search
    friends_list_privacy = models.CharField(
        max_length=20,
        choices=[
            ('PUBLIC', 'Public'),
            ('FRIENDS', 'Friends Only'),
            ('PRIVATE', 'Private'),
        ],
        default='PUBLIC'
    )
    dating_list_privacy = models.CharField(
        max_length=20,
        choices=[
            ('PUBLIC', 'Public'),
            ('FRIENDS', 'Friends Only'),
            ('PRIVATE', 'Private'),
        ],
        default='FRIENDS'
    )

    # Statistics
    posts_count = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def age(self):
        """Calculate age from date of birth."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def get_friends(self):
        """Get list of accepted friends."""
        from messaging.models import Friendship
        sent_friendships = Friendship.objects.filter(
            sender=self.user,
            status='ACCEPTED'
        ).select_related('receiver')
        received_friendships = Friendship.objects.filter(
            receiver=self.user,
            status='ACCEPTED'
        ).select_related('sender')

        friends = []
        for friendship in sent_friendships:
            friends.append(friendship.receiver)
        for friendship in received_friendships:
            friends.append(friendship.sender)
        return friends

    def get_dating_relationships(self):
        """Get list of accepted dating relationships."""
        from dating.models import MatchRequest
        sent_matches = MatchRequest.objects.filter(
            sender=self.user,
            status='ACCEPTED'
        ).select_related('receiver')
        received_matches = MatchRequest.objects.filter(
            receiver=self.user,
            status='ACCEPTED'
        ).select_related('sender')

        dating = []
        for match in sent_matches:
            dating.append(match.receiver)
        for match in received_matches:
            dating.append(match.sender)
        return dating

    def get_knowing_relationships(self):
        """Get list of people you're knowing each other with."""
        from dating.models import MatchRequest
        sent_matches = MatchRequest.objects.filter(
            sender=self.user,
            status='KNOWING'
        ).select_related('receiver')
        received_matches = MatchRequest.objects.filter(
            receiver=self.user,
            status='KNOWING'
        ).select_related('sender')

        knowing = []
        for match in sent_matches:
            knowing.append(match.receiver)
        for match in received_matches:
            knowing.append(match.sender)
        return knowing

    def is_friend_with(self, user):
        """Check if user is friends with another user."""
        from messaging.models import Friendship
        return Friendship.objects.filter(
            models.Q(sender=self.user, receiver=user) |
            models.Q(sender=user, receiver=self.user),
            status='ACCEPTED'
        ).exists()


class OTPVerification(TimeStampedModel):
    """
    Model to store OTP codes for email verification.
    OTPs expire after a configurable time period.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otp_verifications'
    )
    code = models.CharField(
        max_length=6,
        validators=[MinLengthValidator(6)]
    )
    purpose = models.CharField(
        max_length=50,
        choices=[
            ('signup', 'Signup Verification'),
            ('password_reset', 'Password Reset'),
            ('email_change', 'Email Change'),
            ('two_factor', 'Two Factor Authentication'),
        ],
        default='signup'
    )
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'otp_verifications'
        verbose_name = 'OTP Verification'
        verbose_name_plural = 'OTP Verifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['code', 'is_used']),
        ]

    def __str__(self):
        return f"OTP for {self.user.email} - {self.purpose}"

    @classmethod
    def create_otp(cls, user, purpose='signup'):
        """
        Create a new OTP for a user.

        Args:
            user: User instance
            purpose: Purpose of the OTP

        Returns:
            OTPVerification: Created OTP instance
        """
        from django.utils import timezone
        from datetime import timedelta

        code = generate_otp()
        expiry_minutes = settings.OTP_EXPIRY_MINUTES
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

        return cls.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )

    def is_expired(self):
        """Check if the OTP has expired."""
        return is_otp_expired(self.created_at, settings.OTP_EXPIRY_MINUTES)

    def verify(self, code):
        """
        Verify the OTP code.

        Args:
            code: OTP code to verify

        Returns:
            bool: True if verification successful, False otherwise
        """
        if self.is_used:
            return False

        if self.is_expired():
            return False

        if self.code != code:
            return False

        self.is_used = True
        self.save()
        return True
