"""
Repository layer for User app.
Handles data access and abstracts database operations from business logic.
"""

from typing import Optional, List
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import UserProfile, OTPVerification
from core.exceptions import UserNotFoundException, UserAlreadyExistsException

User = get_user_model()


class UserRepository:
    """
    Repository for User data access.
    Provides methods for CRUD operations and queries on User model.
    """

    @staticmethod
    def create(email: str, username: str, password: str, **kwargs) -> User:
        """
        Create a new user.

        Args:
            email: User's email address
            username: User's username
            password: User's password (will be hashed)
            **kwargs: Additional user fields

        Returns:
            User: Created user instance

        Raises:
            UserAlreadyExistsException: If user with email or username already exists
        """
        if User.objects.filter(email=email).exists():
            raise UserAlreadyExistsException(f"User with email {email} already exists")

        if User.objects.filter(username=username).exists():
            raise UserAlreadyExistsException(f"User with username {username} already exists")

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            **kwargs
        )
        return user

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's ID

        Returns:
            Optional[User]: User instance or None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User's email address

        Returns:
            Optional[User]: User instance or None
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: User's username

        Returns:
            Optional[User]: User instance or None
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_email_or_username(identifier: str) -> Optional[User]:
        """
        Get user by email or username.

        Args:
            identifier: Email or username

        Returns:
            Optional[User]: User instance or None
        """
        try:
            return User.objects.get(Q(email=identifier) | Q(username=identifier))
        except User.DoesNotExist:
            return None

    @staticmethod
    def update(user: User, **kwargs) -> User:
        """
        Update user fields.

        Args:
            user: User instance to update
            **kwargs: Fields to update

        Returns:
            User: Updated user instance
        """
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def delete(user: User) -> None:
        """
        Delete a user.

        Args:
            user: User instance to delete
        """
        user.delete()

    @staticmethod
    def verify_user(user: User) -> User:
        """
        Mark user as verified.

        Args:
            user: User instance to verify

        Returns:
            User: Updated user instance
        """
        user.is_verified = True
        user.save()
        return user

    @staticmethod
    def get_all_users(limit: int = None, offset: int = 0) -> List[User]:
        """
        Get all users with pagination.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List[User]: List of user instances
        """
        queryset = User.objects.all()[offset:]
        if limit:
            queryset = queryset[:limit]
        return list(queryset)

    @staticmethod
    def search_users(query: str, limit: int = 20) -> List[User]:
        """
        Search users by username, email, or name.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List[User]: List of matching user instances
        """
        return list(
            User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )[:limit]
        )


class UserProfileRepository:
    """
    Repository for UserProfile data access.
    """

    @staticmethod
    def get_by_user(user: User) -> Optional[UserProfile]:
        """
        Get profile for a user.

        Args:
            user: User instance

        Returns:
            Optional[UserProfile]: UserProfile instance or None
        """
        try:
            return UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return None

    @staticmethod
    def update(profile: UserProfile, **kwargs) -> UserProfile:
        """
        Update user profile.

        Args:
            profile: UserProfile instance to update
            **kwargs: Fields to update

        Returns:
            UserProfile: Updated profile instance
        """
        for key, value in kwargs.items():
            setattr(profile, key, value)
        profile.save()
        return profile


class OTPRepository:
    """
    Repository for OTPVerification data access.
    """

    @staticmethod
    def create(user: User, purpose: str = 'signup') -> OTPVerification:
        """
        Create a new OTP for a user.

        Args:
            user: User instance
            purpose: Purpose of the OTP

        Returns:
            OTPVerification: Created OTP instance
        """
        return OTPVerification.create_otp(user, purpose)

    @staticmethod
    def get_latest_unused(user: User, purpose: str = 'signup') -> Optional[OTPVerification]:
        """
        Get the latest unused OTP for a user and purpose.

        Args:
            user: User instance
            purpose: Purpose of the OTP

        Returns:
            Optional[OTPVerification]: OTP instance or None
        """
        try:
            return OTPVerification.objects.filter(
                user=user,
                purpose=purpose,
                is_used=False
            ).latest('created_at')
        except OTPVerification.DoesNotExist:
            return None

    @staticmethod
    def mark_as_used(otp: OTPVerification) -> OTPVerification:
        """
        Mark an OTP as used.

        Args:
            otp: OTPVerification instance

        Returns:
            OTPVerification: Updated OTP instance
        """
        otp.is_used = True
        otp.save()
        return otp

    @staticmethod
    def delete_expired(user: User) -> int:
        """
        Delete all expired OTPs for a user.

        Args:
            user: User instance

        Returns:
            int: Number of OTPs deleted
        """
        from django.utils import timezone
        count, _ = OTPVerification.objects.filter(
            user=user,
            expires_at__lt=timezone.now()
        ).delete()
        return count
