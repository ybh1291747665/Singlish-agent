from redis.asyncio import Redis
from redis.exceptions import RedisError

from singlish_agent_api.core.config import settings


def get_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def check_redis() -> bool:
    client = get_redis_client()
    try:
        return bool(await client.ping())
    except (OSError, RedisError):
        return False
    finally:
        await client.aclose()
