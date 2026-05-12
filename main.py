"""
Main entry point for the Exam Orchestrator API service.

Initializes the FastAPI application, configures exception handlers,
registers API routers, and manages the application lifecycle.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

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
from api.v1.utils.scheduler import start_scheduler, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages application startup and shutdown events.

    Establishes a connection to the MongoDB database during startup and
    ensures the connection is gracefully closed when the application stops.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control back to the FastAPI framework.
    """
    await connect_and_init_mongo_db()
    start_scheduler()
    yield
    await close_monbgodb_connection()
    scheduler.shutdown()



app: FastAPI = FastAPI(lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_manager)
app.add_exception_handler(Exception, default_exception_manager)

app.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8010,
    )
