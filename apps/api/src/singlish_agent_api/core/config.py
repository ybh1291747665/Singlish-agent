from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    init_db_on_startup: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/singlish_agent"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
