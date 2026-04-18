from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.v1 import v1_router
from api.v1.utils import (
    AppException,
    app_exception_manager,
    default_exception_manager,
    connect_and_init_mongo_db,
    close_monbgodb_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — connect & init DB (fails fast if unreachable)
    await connect_and_init_mongo_db()
    yield
    # SHUTDOWN — close connection
    await close_monbgodb_connection()


app = FastAPI(debug=False, lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_manager)
app.add_exception_handler(Exception, default_exception_manager)

app.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8010,
    )
