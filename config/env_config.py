from pydantic_settings import BaseSettings


class EnvFile(BaseSettings):
    MONGO_URL: str
    MONGO_DB_NAME: str
    DOC_PARSER_URL: str
    EXGATE_UPLOAD_URL: str
    EXGATE_LLM_URL: str

    class Config:
        env_file = ".env"

"""An instance of the EnvFile class, providing access to the environment variables."""
env = EnvFile()