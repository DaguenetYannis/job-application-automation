import pytest

from src.models import JobInput


def test_job_input_rejects_empty_job_title() -> None:
    with pytest.raises(ValueError, match="job_title"):
        JobInput(job_title="   ", company=None, job_description="A real description")


def test_job_input_rejects_empty_job_description() -> None:
    with pytest.raises(ValueError, match="job_description"):
        JobInput(job_title="Data Analyst", company=None, job_description="   ")


def test_job_input_accepts_missing_company() -> None:
    job_input = JobInput(
        job_title="Data Analyst",
        company=None,
        job_description="Analyze useful data.",
    )

    assert job_input.company is None


def test_job_input_trims_whitespace() -> None:
    job_input = JobInput(
        job_title="  Data Analyst  ",
        company="  Acme  ",
        job_description="  Analyze useful data.  ",
    )

    assert job_input.job_title == "Data Analyst"
    assert job_input.company == "Acme"
    assert job_input.job_description == "Analyze useful data."
