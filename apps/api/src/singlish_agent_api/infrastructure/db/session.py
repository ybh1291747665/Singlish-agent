from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from singlish_agent_api.core.config import settings
from singlish_agent_api.domain.jobs import models as job_models  # noqa: F401
from singlish_agent_api.infrastructure.db.base import Base


engine = create_async_engine(settings.database_url, future=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        if engine.dialect.name == "postgresql":
            await connection.execute(
                text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS result_payload TEXT")
            )
