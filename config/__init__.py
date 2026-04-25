"""
Configuration package for the Exam Orchestrator.

Exposes global configuration objects for environment variables and
database settings used throughout the application.
"""

from .db_config import mongodb_config
from .env_config import env

__all__ = ["env", "mongodb_config"]
