from src.models import ParsedJob
from src.parser import JobParser


def test_parser_detects_french_text() -> None:
    text = "Nous recherchons une personne pour ce poste. Vous aurez une mission et des compétences utiles."

    parsed = JobParser().parse(text)

    assert parsed.language == "fr"


def test_parser_detects_english_text() -> None:
    text = "We are hiring for this role. You will own responsibilities and need strong skills."

    parsed = JobParser().parse(text)

    assert parsed.language == "en"


def test_parser_returns_unknown_for_ambiguous_text() -> None:
    parsed = JobParser().parse("Analytics, models, datasets.")

    assert parsed.language == "unknown"


def test_parser_returns_parsed_job_object() -> None:
    parsed = JobParser().parse("We need skills and responsibilities.")

    assert isinstance(parsed, ParsedJob)


def test_parser_detects_bi_reporting_category() -> None:
    text = "Nous recherchons un analyste Power BI pour construire des dashboards, KPI, reporting et Power Query."

    parsed = JobParser().parse(text)

    assert parsed.detected_role_categories[0] == "02_bi_reporting_analytics"


def test_parser_detects_public_policy_statistics_category() -> None:
    text = "Poste en ministère sur les statistiques publiques, indicateurs, politiques publiques et données territoriales."

    parsed = JobParser().parse(text)

    assert "03_public_policy_statistics" in parsed.detected_role_categories


def test_parser_detects_climate_category() -> None:
    text = "Climate and ESG role focused on carbon emissions, GHG Protocol, SBTi and sustainability reporting."

    parsed = JobParser().parse(text)

    assert parsed.detected_role_categories[0] == "05_climate_transition_sustainability"


def test_parser_extracts_required_skills() -> None:
    text = "You will use SQL, Python, Power BI and BigQuery for KPI reporting."

    parsed = JobParser().parse(text)

    assert "SQL" in parsed.detected_required_skills
    assert "Python" in parsed.detected_required_skills
    assert "Power BI" in parsed.detected_required_skills
