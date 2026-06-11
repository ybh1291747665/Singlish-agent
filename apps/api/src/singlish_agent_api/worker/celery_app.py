from celery import Celery

from singlish_agent_api.core.config import settings


celery_app = Celery(
    "singlish_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["singlish_agent_api.worker.tasks"],
)

celery_app.conf.update(
    task_always_eager=settings.celery_task_always_eager,
    task_store_eager_result=True,
)
