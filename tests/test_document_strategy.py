from src.document_strategy import DocumentStrategyBuilder
from src.models import JobInput, ParsedJob


def build_context(category: str) -> dict:
    return {
        "selected_role_categories": [category],
        "selected_skill_blocks": [
            {
                "skill_id": "sql",
                "keywords": ["SQL", "BigQuery"],
                "evidence": ["Greenly: BigQuery and PostgreSQL on carbon data."],
            }
        ],
        "selected_experience_details": [
            {
                "organization": "Greenly",
                "keywords": ["carbon data", "GHG Protocol"],
                "achievements": ["Reporting materials for clients."],
                "evidence": {"tools": ["SQL"], "datasets": ["carbon data"], "methods": [], "outputs": ["reporting"], "domain": []},
            }
        ],
        "selected_project_details": [
            {
                "name": "Transition industrielle verte - Memoire de Master",
                "keywords": ["green transition"],
                "evidence": {"tools": [], "datasets": ["input-output data"], "methods": [], "outputs": [], "domain": []},
            }
        ],
    }


def build_strategy(category: str) -> dict:
    job_input = JobInput("Analyst", "Acme", "SQL reporting climate econometrics.")
    parsed_job = ParsedJob(language="en", detected_role_categories=[category], detected_required_skills=["SQL"])
    return DocumentStrategyBuilder().build(job_input, parsed_job, build_context(category))


def test_bi_role_builds_bi_positioning() -> None:
    strategy = build_strategy("02_bi_reporting_analytics")
    assert "Power BI" in strategy["primary_positioning"]


def test_economist_role_builds_economist_positioning() -> None:
    strategy = build_strategy("04_economist_policy_analyst")
    assert "junior economist" in strategy["primary_positioning"]


def test_climate_role_builds_climate_positioning() -> None:
    strategy = build_strategy("05_climate_transition_sustainability")
    assert "climate transition" in strategy["primary_positioning"]


def test_strategy_includes_quality_targets() -> None:
    strategy = build_strategy("02_bi_reporting_analytics")
    assert strategy["quality_targets"]["min_experience_bullets"] == 4
    assert strategy["quality_targets"]["include_all_languages"] is True


def test_strategy_includes_must_include_evidence() -> None:
    strategy = build_strategy("02_bi_reporting_analytics")
    assert strategy["must_include_evidence"]
    assert any("SQL" in item for item in strategy["must_include_evidence"])
