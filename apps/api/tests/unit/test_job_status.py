from singlish_agent_api.domain.jobs.models import JobStatus, can_transition


def test_job_status_allows_expected_forward_transition() -> None:
    assert can_transition(JobStatus.CREATED, JobStatus.UPLOADED) is True
    assert can_transition(JobStatus.UPLOADED, JobStatus.QUEUED) is True
    assert can_transition(JobStatus.QUEUED, JobStatus.PROCESSING) is True
    assert can_transition(JobStatus.PROCESSING, JobStatus.COMPLETED) is True


def test_job_status_blocks_invalid_transition() -> None:
    assert can_transition(JobStatus.CREATED, JobStatus.COMPLETED) is False
