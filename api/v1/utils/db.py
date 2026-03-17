import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config import mongodb_config

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_and_init_db():
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
            print(f"Connected to MongoDB at {mongodb_config.MONGO_URL}")
            break
        except (ConnectionFailure, ServerSelectionTimeoutError):
            elapsed += retry_interval
            print(
                f"MongoDB not ready, retrying in {retry_interval}s... "
                f"({elapsed}/{max_retry_seconds}s)"
            )
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
            print(f"Created collection: {col_name}")
        else:
            print(f"Collection already exists: {col_name}")

    for col_name, index_list in mongodb_config.INDEXES.items():
        for field, unique in index_list:
            await db[col_name].create_index(field, unique=unique)
            print(f"Index on {col_name}.{field} (unique={unique})")


async def close_db_connection():
    """Gracefully close the MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency — returns the db handle or raises 503."""
    if db is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available",
        )
    return db