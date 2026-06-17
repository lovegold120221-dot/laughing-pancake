from functools import lru_cache
from os import getenv


class Settings:
    def __init__(self) -> None:
        self.translation_api_key = (
            getenv("EBURON_GOOGLE_API_KEY")
            or getenv("GOOGLE_API_KEY")
            or getenv("GOOGLE_CLOUD_API_KEY")
            or ""
        )
        self.translation_api_timeout_seconds = float(
            getenv("EBURON_TRANSLATE_API_TIMEOUT_SECONDS", "15")
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

