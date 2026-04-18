import uvicorn
from pydantic.v1 import BaseSettings

from config import env


class MongoDBConfig(BaseSettings):
    """All MongoDB-related configuration in one place."""

    MONGO_URL: str = env.MONGO_URL
    MONGO_DB_NAME: str = env.MONGO_DB_NAME
    MONGO_TIMEOUT_MS: int = 5000

    COLLECTIONS: dict[str, dict | None] = {
        "exam": {},
        "correction": {},
        "answer_sheet": {},
        "grade": {},
    }


mongodb_config = MongoDBConfig()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8010,
    )
