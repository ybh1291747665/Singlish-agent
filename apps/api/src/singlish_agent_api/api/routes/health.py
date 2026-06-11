import asyncio

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from singlish_agent_api.infrastructure.cache.redis import check_redis
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.storage.client import check_storage

router = APIRouter()


async def check_database() -> bool:
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
            return True
    except (OSError, SQLAlchemyError):
        return False


@router.get("/health")
async def health() -> dict[str, object]:
    database_ok, redis_ok, storage_ok = await asyncio.gather(
        check_database(),
        check_redis(),
        check_storage(),
    )

    services = {
        "app": "ok",
        "database": "ok" if database_ok else "error",
        "redis": "ok" if redis_ok else "error",
        "object_storage": "ok" if storage_ok else "error",
    }
    overall = "ok" if all(value == "ok" for value in services.values()) else "degraded"

    return {
        "status": overall,
        "services": services,
    }
