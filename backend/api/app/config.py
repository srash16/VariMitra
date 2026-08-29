from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://varimitra:varimitra@127.0.0.1:5432/varimitra"
    pairing_pepper: str = "change-me-in-production"
    pairing_ttl_hours: int = 24


settings = Settings()
