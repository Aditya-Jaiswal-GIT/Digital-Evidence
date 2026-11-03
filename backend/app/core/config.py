from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Database
    MONGO_URI: str
    DATABASE_NAME: str = "digital_evidence_db"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()