from src.models import JobInput, ParsedJob
from src.prompt_builder import PromptBuilder


def test_prompt_builder_builds_application_prompt() -> None:
    job_input = JobInput(
        job_title="BI Analyst",
        company="Acme",
        job_description="Power BI, SQL and KPI reporting.",
    )
    parsed_job = ParsedJob(language="en", detected_role_categories=["02_bi_reporting_analytics"])
    selected_context = {
        "selected_role_categories": ["02_bi_reporting_analytics"],
        "selected_skill_blocks": [{"skill_id": "sql", "short": "SQL"}],
    }

    prompt = PromptBuilder().build_application_prompt(job_input, parsed_job, selected_context)

    assert "BI Analyst" in prompt
    assert "02_bi_reporting_analytics" in prompt
    assert "Return only valid JSON" in prompt
    assert "Do not invent facts" in prompt
    assert "Do not use the em dash character" in prompt
    assert chr(8212) not in prompt
