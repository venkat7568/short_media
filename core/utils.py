"""
Utility functions for Short Media Platform.
Provides common helper functions used across the platform.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional
from django.utils import timezone


def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric OTP code.

    Args:
        length: Length of the OTP (default: 6)

    Returns:
        str: Generated OTP code
    """
    return ''.join(random.choices(string.digits, k=length))


def generate_random_string(length: int = 32, include_digits: bool = True,
                          include_special: bool = False) -> str:
    """
    Generate a random alphanumeric string.

    Args:
        length: Length of the string
        include_digits: Whether to include digits
        include_special: Whether to include special characters

    Returns:
        str: Generated random string
    """
    chars = string.ascii_letters
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation

    return ''.join(random.choices(chars, k=length))


def is_otp_expired(created_at: datetime, expiry_minutes: int = 10) -> bool:
    """
    Check if an OTP has expired.

    Args:
        created_at: When the OTP was created
        expiry_minutes: OTP validity period in minutes

    Returns:
        bool: True if OTP has expired, False otherwise
    """
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at)

    expiry_time = created_at + timedelta(minutes=expiry_minutes)
    return timezone.now() > expiry_time


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove potentially dangerous characters.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove path separators and other dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    return filename


def get_file_extension(filename: str) -> Optional[str]:
    """
    Extract file extension from filename.

    Args:
        filename: Filename with extension

    Returns:
        Optional[str]: File extension (lowercase) or None
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return None


def is_image_file(filename: str) -> bool:
    """
    Check if a file is an image based on extension.

    Args:
        filename: Filename to check

    Returns:
        bool: True if file is an image, False otherwise
    """
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'}
    extension = get_file_extension(filename)
    return extension in image_extensions if extension else False


def is_video_file(filename: str) -> bool:
    """
    Check if a file is a video based on extension.

    Args:
        filename: Filename to check

    Returns:
        bool: True if file is a video, False otherwise
    """
    video_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
    extension = get_file_extension(filename)
    return extension in video_extensions if extension else False


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to HH:MM:SS or MM:SS.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration string
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def get_client_ip(request) -> Optional[str]:
    """
    Extract client IP address from Django request.

    Args:
        request: Django request object

    Returns:
        Optional[str]: Client IP address or None
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
