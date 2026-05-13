"""
Environment configuration management for the Exam Orchestrator.

This module defines the schema for environment variables used across the
application, leveraging Pydantic Settings for validation and type safety.
"""

from pydantic_settings import BaseSettings


class EnvFile(BaseSettings):
    """
    Configuration container for environment-based settings.

    Loads and validates configuration parameters from the environment or a .env
    file. Provides typed access to service URLs and database credentials.

    Attributes:
        MONGO_URL: The connection string for the MongoDB instance.
        MONGO_DB_NAME: The name of the primary database for the orchestrator.
        DOC_PARSER_URL: The base URL for the document parsing microservice.
        EXGATE_UPLOAD_URL: The gateway URL for file upload operations.
        EXGATE_LLM_URL: The gateway URL for Large Language Model interactions.
        OCR_URL: The base URL for the OCR processing service.
        ANTICHEAT_URL: The base URL for the anti-cheat verification service.
    """

    MONGO_URL: str
    MONGO_DB_NAME: str
    DOC_PARSER_URL: str
    EXGATE_URL: str
    OCR_URL: str
    ANTICHEAT_URL: str

    class Config:
        """
        Metadata configuration for Pydantic Settings.
        """

        env_file: str = ".env"


env: EnvFile = EnvFile()
