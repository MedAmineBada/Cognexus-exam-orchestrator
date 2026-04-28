"""
Database configuration and initialization settings.

Defines the connection parameters and collection schemas for MongoDB
integration, ensuring consistent data access across the application.
"""

from typing import Dict, Optional

import uvicorn
from pydantic.v1 import BaseSettings

from .env_config import env


class MongoDBConfig(BaseSettings):
    """
    Settings for MongoDB connection and collection management.

    Centralizes database configuration, including connection strings,
    timeouts, and the registry of application collections.

    Attributes:
        MONGO_URL: The MongoDB connection URI retrieved from environment.
        MONGO_DB_NAME: The target database name retrieved from environment.
        MONGO_TIMEOUT_MS: Server selection timeout in milliseconds.
        COLLECTIONS: A mapping of collection names to their configuration.
    """

    MONGO_URL: str = env.MONGO_URL
    MONGO_DB_NAME: str = env.MONGO_DB_NAME
    MONGO_TIMEOUT_MS: int = 5000

    COLLECTIONS: Dict[str, Optional[Dict]] = {
        "exam": {},
        "correction": {},
        "answer_sheet": {},
        "grade": {},
    }


mongodb_config: MongoDBConfig = MongoDBConfig()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8010,
    )
