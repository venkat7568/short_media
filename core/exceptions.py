"""
Custom exceptions for Short Media Platform.
Provides domain-specific exceptions for better error handling.
"""


class ShortMediaException(Exception):
    """Base exception for all Short Media Platform exceptions."""

    def __init__(self, message: str = None, code: str = None):
        self.message = message or "An error occurred"
        self.code = code or "UNKNOWN_ERROR"
        super().__init__(self.message)


class AuthenticationException(ShortMediaException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class InvalidOTPException(AuthenticationException):
    """Raised when OTP verification fails."""

    def __init__(self, message: str = "Invalid or expired OTP"):
        super().__init__(message)
        self.code = "INVALID_OTP"


class UserAlreadyExistsException(ShortMediaException):
    """Raised when trying to create a user that already exists."""

    def __init__(self, message: str = "User already exists"):
        super().__init__(message, "USER_EXISTS")


class UserNotFoundException(ShortMediaException):
    """Raised when a user is not found."""

    def __init__(self, message: str = "User not found"):
        super().__init__(message, "USER_NOT_FOUND")


class PermissionDeniedException(ShortMediaException):
    """Raised when user doesn't have permission for an action."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "PERMISSION_DENIED")


class ResourceNotFoundException(ShortMediaException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, message: str = None):
        message = message or f"{resource_type} not found"
        super().__init__(message, "RESOURCE_NOT_FOUND")
        self.resource_type = resource_type


class NotFoundException(ShortMediaException):
    """Raised when an entity is not found."""

    def __init__(self, message: str = "Not found"):
        super().__init__(message, "NOT_FOUND")


class ValidationException(ShortMediaException):
    """Raised when data validation fails."""

    def __init__(self, message: str = "Validation failed", errors: dict = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.errors = errors or {}


class ServiceException(ShortMediaException):
    """Raised when a service operation fails."""

    def __init__(self, service_name: str, message: str = None):
        message = message or f"{service_name} operation failed"
        super().__init__(message, "SERVICE_ERROR")
        self.service_name = service_name


class ExternalServiceException(ShortMediaException):
    """Raised when an external service (email, SMS, etc.) fails."""

    def __init__(self, service_name: str, message: str = None):
        message = message or f"{service_name} service unavailable"
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name


class InvalidStateTransitionException(ShortMediaException):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, from_state: str, to_state: str, message: str = None):
        message = message or f"Invalid transition from {from_state} to {to_state}"
        super().__init__(message, "INVALID_STATE_TRANSITION")
        self.from_state = from_state
        self.to_state = to_state
