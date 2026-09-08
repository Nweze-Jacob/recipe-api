from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    """Application configuration loaded from environment variables
    and the .env file"""

    PROJECT_NAME: str = "Recipe API"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str

    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()