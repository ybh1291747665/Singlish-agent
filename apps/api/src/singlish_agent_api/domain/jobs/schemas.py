from datetime import datetime

from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    job_id: str
    file_name: str
    status: str
    created_at: datetime


class JobDetailResponse(BaseModel):
    job_id: str
    file_name: str
    status: str
    result_summary: str | None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None
