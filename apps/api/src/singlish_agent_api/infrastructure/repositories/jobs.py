import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from singlish_agent_api.domain.jobs.models import Job, JobStatus, can_transition


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, file_name: str, object_key: str) -> Job:
        job = Job(file_name=file_name, object_key=object_key, status=JobStatus.CREATED.value)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get(self, job_id: str) -> Job | None:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def transition(self, job: Job, target: JobStatus) -> Job:
        current = JobStatus(job.status)
        if not can_transition(current, target):
            raise ValueError(f"invalid transition: {current} -> {target}")
        job.status = target.value
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def set_result(self, job: Job, *, summary: str) -> Job:
        job.result_summary = summary
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def set_result_payload(self, job: Job, *, payload: dict[str, object]) -> Job:
        job.result_payload = json.dumps(payload)
        await self.session.commit()
        await self.session.refresh(job)
        return job
