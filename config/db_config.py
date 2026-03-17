from pydantic.v1 import BaseSettings

from config import env


class MongoDBConfig(BaseSettings):
    """All MongoDB-related configuration in one place."""

    MONGO_URL: str = env.MONGO_URL
    MONGO_DB_NAME: str = env.MONGO_DB_NAME
    MONGO_TIMEOUT_MS: int = 5000

    COLLECTIONS: dict[str, dict | None] = {
        "exam": {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "_id",
                        "exam_title",
                        "teacher_id",
                        "publish_time",
                        "content",
                        "correction_id",
                        "url"
                    ],
                    "properties": {
                        "_id": {"bsonType": "int"},
                        "exam_title": {"bsonType": "string"},
                        "teacher_id": {"bsonType": "int"},
                        "publish_time": {"bsonType": "date"},
                        "content": {"bsonType": "object"},  # JSON
                        "correction_id": {"bsonType": "int"},
                        "url": {"bsonType": "string"}
                    }
                }
            }
        },

        "correction": {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "_id",
                        "exam_id",
                        "url",
                        "content"
                    ],
                    "properties": {
                        "_id": {"bsonType": "int"},
                        "exam_id": {"bsonType": "int"},
                        "url": {"bsonType": "string"},
                        "content": {"bsonType": "object"}
                    }
                }
            }
        },

        "answer_sheet": {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "_id",
                        "student_id",
                        "exam_id",
                        "content",
                        "url"
                    ],
                    "properties": {
                        "_id": {"bsonType": "int"},
                        "student_id": {"bsonType": "int"},
                        "exam_id": {"bsonType": "int"},
                        "content": {"bsonType": "object"},
                        "url": {"bsonType": "string"}
                    }
                }
            }
        }
    }

    INDEXES: dict[str, list[tuple[str, bool]]] = {
        "exam": [
            ("teacher_id", False),
        ],
        "correction": [("exam_id", False)],
        "answer_sheet": [
            ("exam_id", False),
            ("student_id", False),
        ],
    }


mongodb_config = MongoDBConfig()