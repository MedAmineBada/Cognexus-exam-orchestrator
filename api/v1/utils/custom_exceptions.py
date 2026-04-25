from starlette import status


class AppException(Exception):
    """
    Base exception class for application-specific errors.

    Attributes:
        message: A descriptive error message.
        status_code: The HTTP status code associated with the error.
    """
    def __init__(
        self,
        message: str = "Something went wrong.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BadGatewayException(AppException):
    """
    Exception raised when an external service returns an invalid response.
    """
    def __init__(
        self,
        message: str = "Bad Gateway",
        status_code: int = status.HTTP_502_BAD_GATEWAY,
    ) -> None:
        super().__init__(message, status_code)


class GatewayTimeoutException(AppException):
    """
    Exception raised when an external service request times out.
    """
    def __init__(
        self,
        message: str = "Gateway Timeout",
        status_code: int = status.HTTP_504_GATEWAY_TIMEOUT,
    ) -> None:
        super().__init__(message, status_code)


class NotFoundException(AppException):
    """
    Exception raised when a requested resource is not found.
    """
    def __init__(
        self,
        message: str = "Not Found",
        status_code: int = status.HTTP_404_NOT_FOUND
    ) -> None:
        super().__init__(message, status_code)


class ConflictException(AppException):
    """
    Exception raised when a request conflicts with the current state of the server.
    """
    def __init__(
        self,
        message: str = "Conflict",
        status_code: int = status.HTTP_409_CONFLICT
    ) -> None:
        super().__init__(message, status_code)


class ForbiddenException(AppException):
    """
    Exception raised when a user is not authorized to perform an action.
    """
    def __init__(
        self,
        message: str = "Forbidden",
        status_code: int = status.HTTP_403_FORBIDDEN
    ) -> None:
        super().__init__(message, status_code)
