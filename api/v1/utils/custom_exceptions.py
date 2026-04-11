from starlette import status

class AppException(Exception):
    def __init__(self, message: str = "Something went wrong.", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class BadGatewayException(AppException):
    def __init__(self, message: str = "Bad Gateway", status_code: int = status.HTTP_502_BAD_GATEWAY):
        super().__init__(message, status_code)

class GatewayTimeoutException(AppException):
    def __init__(self, message: str = "Gateway Timeout", status_code: int = status.HTTP_504_GATEWAY_TIMEOUT):
        super().__init__(message, status_code)
