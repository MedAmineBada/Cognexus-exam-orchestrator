from starlette import status
from starlette.responses import JSONResponse

async def app_exception_manager(req, exc):
    return JSONResponse(content={"error": exc.message}, status_code=exc.status_code)

async def default_exception_manager(req, exc):
    return JSONResponse(content={"error": "Something went wrong."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
