from src.models import ParsedJob
from src.requirement_mapper import RequirementMapper


def context() -> dict:
    return {
        "selected_skill_blocks": [
            {"skill_id": "sql", "evidence": ["Greenly BigQuery", "DataForGood DuckDB"]},
            {"skill_id": "econometrics", "evidence": ["Dauphine econometrics"]},
        ],
        "selected_experience_details": [
            {"organization": "Greenly", "achievements": ["client reporting slides"]},
            {"organization": "DataForGood / Reclaim Finance", "achievements": ["DuckDB pipeline"]},
        ],
        "candidate_education": [
            {"institution": "Universite Paris Dauphine"},
            {"institution": "Maastricht University"},
        ],
        "candidate_languages": [{"language": "English", "level": "C2"}],
    }


def mapping_for(description_terms: list[str]) -> list[dict]:
    parsed = ParsedJob(
        language="en",
        detected_required_skills=description_terms,
        detected_keywords=description_terms,
    )
    return RequirementMapper().build_mapping(parsed, context())


def evidence_for(requirement: str, mappings: list[dict]) -> list[str]:
    for mapping in mappings:
        if mapping["job_requirement"] == requirement:
            return mapping["candidate_evidence"]
    return []


def test_sql_maps_to_greenly_dataforgood_evidence() -> None:
    evidence = evidence_for("SQL", mapping_for(["SQL"]))
    assert any("Greenly" in item for item in evidence)
    assert any("DataForGood" in item for item in evidence)


def test_econometrics_maps_to_dauphine_statistical_evidence() -> None:
    evidence = evidence_for("econometrics/statistics", mapping_for(["econometrics", "statistics"]))
    assert any("Dauphine" in item for item in evidence)
    assert any("statistical" in item for item in evidence)


def test_reporting_maps_to_greenly_reporting_evidence() -> None:
    evidence = evidence_for("Power BI/dashboard/reporting", mapping_for(["reporting"]))
    assert any("Greenly" in item and "reporting" in item for item in evidence)


def test_international_environment_maps_to_maastricht_english_evidence() -> None:
    evidence = evidence_for("international environment", mapping_for(["international environment", "English"]))
    assert any("Maastricht" in item for item in evidence)
    assert any("English C2" in item for item in evidence)
