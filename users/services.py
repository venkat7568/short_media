"""
Service layer for User app.
Implements business logic for authentication, user management, and email services.
"""

from typing import Optional, Tuple
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .repositories import UserRepository, UserProfileRepository, OTPRepository
from core.exceptions import (
    AuthenticationException,
    InvalidOTPException,
    UserAlreadyExistsException,
    UserNotFoundException,
    ExternalServiceException,
)


class EmailService:
    """
    Service for sending emails.
    Handles OTP emails, welcome emails, and other notifications.
    """

    @staticmethod
    def send_otp_email(user: User, otp_code: str) -> bool:
        """
        Send OTP verification email to user.

        Args:
            user: User instance
            otp_code: OTP code to send

        Returns:
            bool: True if email sent successfully, False otherwise

        Raises:
            ExternalServiceException: If email sending fails
        """
        try:
            subject = f'Your OTP Code - {settings.SITE_NAME}'

            # Create HTML email content
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #00C851; color: white; padding: 20px; text-align: center; }}
                    .content {{ background-color: #f9f9f9; padding: 30px; }}
                    .otp-code {{ font-size: 32px; font-weight: bold; color: #00C851; text-align: center;
                                 letter-spacing: 5px; padding: 20px; background-color: white;
                                 border: 2px dashed #00C851; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; padding: 20px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{settings.SITE_NAME}</h1>
                    </div>
                    <div class="content">
                        <h2>Hello {user.username}!</h2>
                        <p>Your OTP verification code is:</p>
                        <div class="otp-code">{otp_code}</div>
                        <p>This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes.</p>
                        <p>If you didn't request this code, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 {settings.SITE_NAME}. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            raise ExternalServiceException(
                'Email',
                f'Failed to send OTP email: {str(e)}'
            )

    @staticmethod
    def send_welcome_email(user: User) -> bool:
        """
        Send welcome email to newly verified user.

        Args:
            user: User instance

        Returns:
            bool: True if email sent successfully

        Raises:
            ExternalServiceException: If email sending fails
        """
        try:
            subject = f'Welcome to {settings.SITE_NAME}!'

            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #00C851; color: white; padding: 20px; text-align: center; }}
                    .content {{ background-color: #f9f9f9; padding: 30px; }}
                    .button {{ background-color: #00C851; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 5px; display: inline-block;
                              margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; padding: 20px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to {settings.SITE_NAME}!</h1>
                    </div>
                    <div class="content">
                        <h2>Hello {user.get_full_name() or user.username}!</h2>
                        <p>Your account has been successfully verified. Welcome to our community!</p>
                        <p>You can now:</p>
                        <ul>
                            <li>Create and share posts</li>
                            <li>Connect with other users</li>
                            <li>Find matches</li>
                            <li>Start video calls</li>
                        </ul>
                        <a href="{settings.SITE_URL}" class="button">Get Started</a>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 {settings.SITE_NAME}. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Don't raise exception for welcome email failure
            print(f"Failed to send welcome email: {str(e)}")
            return False


class AuthenticationService:
    """
    Service for user authentication and registration.
    Implements signup, login, OTP verification, and token management.
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.otp_repo = OTPRepository()
        self.email_service = EmailService()

    def signup(self, email: str, username: str, password: str, **kwargs) -> Tuple[User, str]:
        """
        Register a new user and send OTP verification email.

        Args:
            email: User's email address
            username: User's username
            password: User's password
            **kwargs: Additional user fields

        Returns:
            Tuple[User, str]: Created user and OTP code

        Raises:
            UserAlreadyExistsException: If user already exists
            ExternalServiceException: If email sending fails
        """
        # Create user
        user = self.user_repo.create(email, username, password, **kwargs)

        # Create OTP
        otp = self.otp_repo.create(user, purpose='signup')

        # Send OTP email
        self.email_service.send_otp_email(user, otp.code)

        return user, otp.code

    def verify_otp(self, user: User, otp_code: str, purpose: str = 'signup') -> bool:
        """
        Verify OTP code for a user.

        Args:
            user: User instance
            otp_code: OTP code to verify
            purpose: Purpose of the OTP

        Returns:
            bool: True if verification successful

        Raises:
            InvalidOTPException: If OTP is invalid or expired
        """
        # Get latest unused OTP
        otp = self.otp_repo.get_latest_unused(user, purpose)

        if not otp:
            raise InvalidOTPException("No OTP found for this user")

        # Verify OTP
        if not otp.verify(otp_code):
            raise InvalidOTPException("Invalid or expired OTP")

        # Mark user as verified if signup OTP
        if purpose == 'signup':
            self.user_repo.verify_user(user)
            # Send welcome email
            self.email_service.send_welcome_email(user)

        return True

    def resend_otp(self, user: User, purpose: str = 'signup') -> str:
        """
        Resend OTP to user.

        Args:
            user: User instance
            purpose: Purpose of the OTP

        Returns:
            str: New OTP code

        Raises:
            ExternalServiceException: If email sending fails
        """
        # Delete expired OTPs
        self.otp_repo.delete_expired(user)

        # Create new OTP
        otp = self.otp_repo.create(user, purpose)

        # Send OTP email
        self.email_service.send_otp_email(user, otp.code)

        return otp.code

    def login(self, email_or_username: str, password: str) -> Tuple[User, dict]:
        """
        Authenticate user and generate JWT tokens.

        Args:
            email_or_username: User's email or username
            password: User's password

        Returns:
            Tuple[User, dict]: User instance and tokens dict

        Raises:
            AuthenticationException: If authentication fails
        """
        # Get user
        user = self.user_repo.get_by_email_or_username(email_or_username)

        if not user:
            raise AuthenticationException("Invalid credentials")

        # Check password
        if not user.check_password(password):
            raise AuthenticationException("Invalid credentials")

        # Check if user is verified
        if not user.is_verified:
            raise AuthenticationException("Please verify your email first")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return user, tokens

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User's email address

        Returns:
            Optional[User]: User instance or None
        """
        return self.user_repo.get_by_email(email)

    def change_password(self, user: User, old_password: str, new_password: str) -> bool:
        """
        Change user's password.

        Args:
            user: User instance
            old_password: Current password
            new_password: New password

        Returns:
            bool: True if password changed successfully

        Raises:
            AuthenticationException: If old password is incorrect
        """
        if not user.check_password(old_password):
            raise AuthenticationException("Incorrect current password")

        user.set_password(new_password)
        user.save()
        return True


class ProfileService:
    """
    Service for user profile management.
    """

    def __init__(self):
        self.profile_repo = UserProfileRepository()

    def update_profile(self, user: User, **kwargs) -> bool:
        """
        Update user profile.

        Args:
            user: User instance
            **kwargs: Fields to update

        Returns:
            bool: True if update successful
        """
        profile = self.profile_repo.get_by_user(user)
        if profile:
            self.profile_repo.update(profile, **kwargs)
            return True
        return False

    def get_profile(self, user: User):
        """
        Get user profile.

        Args:
            user: User instance

        Returns:
            UserProfile: User's profile
        """
        return self.profile_repo.get_by_user(user)
