from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    init_db_on_startup: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/singlish_agent"
    redis_url: str = "redis://127.0.0.1:6379/0"
    s3_endpoint_url: str = "http://127.0.0.1:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "singlish-agent"
    s3_region: str = "us-east-1"
    celery_task_always_eager: bool = False
    asr_backend: str = "auto"
    asr_model_size: str = "tiny.en"
    asr_device: str = "cpu"
    asr_compute_type: str = "int8"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
