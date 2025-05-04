import logging
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    google_api_key: str = ""
    serper_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        extra="ignore",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        env_file_path = self.model_config.get("env_file")
        if not env_file_path:
            logger.warning(
                ".env file not found. Relying on system environment variables."
            )
        else:
            logger.info(f"Loaded settings from: {env_file_path}")

        if not self.google_api_key:
            logger.error(
                "CRITICAL: GOOGLE_API_KEY not found in settings after loading."
            )
        else:
            logger.info("GOOGLE_API_KEY found in settings.")

        if not self.serper_api_key:
            logger.error(
                "CRITICAL: SERPER_API_KEY not found in settings after loading."
            )
        else:
            logger.info("SERPER_API_KEY found in settings.")


@lru_cache()
def get_settings() -> Settings:
    logger.info("Loading application settings...")
    return Settings()
