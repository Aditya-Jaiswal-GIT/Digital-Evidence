from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    MONGO_URI: str
    DATABASE_NAME: str = "digital_evidence_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()