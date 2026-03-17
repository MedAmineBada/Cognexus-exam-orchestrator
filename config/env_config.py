from pydantic.v1 import BaseSettings


class EnvFile(BaseSettings):
    MONGO_URL: str
    MONGO_DB_NAME: str

    class Config:
        env_file = ".env"

"""An instance of the EnvFile class, providing access to the environment variables."""
env = EnvFile()