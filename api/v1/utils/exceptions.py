from http.client import HTTPException

from starlette import status
from starlette.responses import JSONResponse


class AppException(HTTPException):
    def __init__(self, message: str = "Something went wrong.", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

async def app_exception_manager(req, exc):
    return JSONResponse(content={"error": exc.message}, status_code=exc.status_code)

async def default_exception_manager(req, exc):
    return JSONResponse(content={"error": "Something went wrong."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)