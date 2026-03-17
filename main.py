from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1 import v1_router
from api.v1.utils import AppException, app_exception_manager, default_exception_manager
from api.v1.utils.db import connect_and_init_db, close_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — connect & init DB (fails fast if unreachable)
    await connect_and_init_db()
    yield
    # SHUTDOWN — close connection
    await close_db_connection()

app = FastAPI(debug=False, lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_manager)
app.add_exception_handler(Exception, default_exception_manager)

app.include_router(v1_router)
