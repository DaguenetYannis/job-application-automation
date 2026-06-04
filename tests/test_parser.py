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
