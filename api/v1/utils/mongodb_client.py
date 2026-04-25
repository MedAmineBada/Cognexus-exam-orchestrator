import asyncio
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config import mongodb_config

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_and_init_mongo_db() -> None:
    """
    Establishes a connection to MongoDB and initializes required collections.

    Performs a health check via ping and retries connection until the timeout
    limit is reached. Once connected, creates collections defined in the
    configuration if they do not already exist.

    Raises:
        RuntimeError: If connection cannot be established within the retry limit.
    """
    global client, db

    client = AsyncIOMotorClient(
        mongodb_config.MONGO_URL,
        serverSelectionTimeoutMS=mongodb_config.MONGO_TIMEOUT_MS,
    )

    max_retry_seconds = 30
    retry_interval = 2
    elapsed = 0

    while elapsed < max_retry_seconds:
        try:
            await client.admin.command("ping")
            break
        except (ConnectionFailure, ServerSelectionTimeoutError):
            elapsed += retry_interval
            await asyncio.sleep(retry_interval)
    else:
        raise RuntimeError(
            f"Could not connect to MongoDB at {mongodb_config.MONGO_URL} "
            f"after {max_retry_seconds}s"
        )

    db = client[mongodb_config.MONGO_DB_NAME]
    existing = await db.list_collection_names()

    for col_name, options in mongodb_config.COLLECTIONS.items():
        if col_name not in existing:
            if options:
                await db.create_collection(col_name, **options)
            else:
                await db.create_collection(col_name)


async def close_monbgodb_connection() -> None:
    """
    Gracefully terminates the active MongoDB client connection.
    """
    global client
    if client:
        client.close()


def get_mongodb() -> AsyncIOMotorDatabase:
    """
    Provides access to the initialized MongoDB database instance.

    Returns:
        The active AsyncIOMotorDatabase handle.

    Raises:
        HTTPException: If the database has not been initialized.
    """
    if db is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available",
        )
    return db


async def get_next_id(collection_name: str) -> int:
    """
    Generates a unique, incrementing integer ID for a specific collection.

    This function uses an atomic 'counters' collection to manage and persist
    the last used ID, starting from zero.

    Args:
        collection_name: The name of the collection for which to generate an ID.

    Returns:
        A unique integer identifier.
    """
    if db is None:
        raise RuntimeError("Database not initialized")

    counter = await db.counters.find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return counter["seq"] - 1
