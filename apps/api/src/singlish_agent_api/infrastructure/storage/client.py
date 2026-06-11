import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from singlish_agent_api.core.config import settings


def get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


async def check_storage() -> bool:
    try:
        get_s3_client().head_bucket(Bucket=settings.s3_bucket)
        return True
    except (BotoCoreError, ClientError):
        return False
