# core/config.py
import os
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Define the environment variables you need
    google_api_key: str = ""  # Default to empty string
    serper_api_key: str = ""  # Add Serper API key

    # Configure Pydantic settings
    model_config = SettingsConfigDict(
        # Load from .env file found by find_dotenv
        env_file=find_dotenv(),
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    logger.info("Loading application settings...")
    env_file_path = find_dotenv()
    if not env_file_path:
        logger.warning(".env file not found. Relying on system environment variables.")
    else:
        logger.info(f"Attempting to load settings from: {env_file_path}")

    settings = Settings()

    # Log whether the key was found after loading
    if not settings.google_api_key:
        logger.error("CRITICAL: GOOGLE_API_KEY not found in settings after loading.")
    else:
        # Avoid logging the actual key value for security
        logger.info("GOOGLE_API_KEY found in settings.")

    return settings


# Instantiate settings once for potential direct import if needed,
# but prefer using the get_settings dependency.
settings = get_settings()
