from singlish_agent_api.domain.jobs.models import JobStatus, can_transition


def test_job_status_allows_expected_forward_transition() -> None:
    assert can_transition(JobStatus.CREATED, JobStatus.UPLOADED) is True
    assert can_transition(JobStatus.UPLOADED, JobStatus.QUEUED) is True
    assert can_transition(JobStatus.QUEUED, JobStatus.PREPROCESSING) is True
    assert can_transition(JobStatus.PREPROCESSING, JobStatus.TRANSCRIBING) is True
    assert can_transition(JobStatus.TRANSCRIBING, JobStatus.NORMALIZING) is True
    assert can_transition(JobStatus.NORMALIZING, JobStatus.GENERATING_REPORT) is True
    assert can_transition(JobStatus.GENERATING_REPORT, JobStatus.COMPLETED) is True


def test_job_status_blocks_invalid_transition() -> None:
    assert can_transition(JobStatus.CREATED, JobStatus.COMPLETED) is False
