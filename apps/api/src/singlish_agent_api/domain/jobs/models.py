from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from singlish_agent_api.infrastructure.db.base import Base


class JobStatus(StrEnum):
    CREATED = "created"
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PREPROCESSING = "preprocessing"
    TRANSCRIBING = "transcribing"
    NORMALIZING = "normalizing"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


ALLOWED_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.CREATED: {JobStatus.UPLOADED},
    JobStatus.UPLOADED: {JobStatus.QUEUED, JobStatus.FAILED},
    JobStatus.QUEUED: {JobStatus.PREPROCESSING, JobStatus.FAILED},
    JobStatus.PREPROCESSING: {JobStatus.TRANSCRIBING, JobStatus.FAILED},
    JobStatus.TRANSCRIBING: {JobStatus.NORMALIZING, JobStatus.FAILED},
    JobStatus.NORMALIZING: {JobStatus.GENERATING_REPORT, JobStatus.FAILED},
    JobStatus.GENERATING_REPORT: {JobStatus.COMPLETED, JobStatus.FAILED},
    JobStatus.COMPLETED: set(),
    JobStatus.FAILED: set(),
}


def can_transition(current: JobStatus, target: JobStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    file_name: Mapped[str] = mapped_column(String(255))
    object_key: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default=JobStatus.CREATED.value)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
