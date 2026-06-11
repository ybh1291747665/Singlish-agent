import asyncio

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from singlish_agent_api.core.config import settings


class ObjectStorageService:
    def __init__(self) -> None:
        self.client = get_s3_client()

    async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=settings.s3_bucket,
            Key=object_key,
            Body=content,
            ContentType=content_type,
        )


def get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(
            connect_timeout=1,
            read_timeout=1,
            retries={"max_attempts": 0},
        ),
    )


async def check_storage() -> bool:
    try:
        await asyncio.to_thread(get_s3_client().head_bucket, Bucket=settings.s3_bucket)
        return True
    except (BotoCoreError, ClientError):
        return False
