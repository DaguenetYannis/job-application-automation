from src.slugifier import Slugifier


def test_slugifier_lowercases_text() -> None:
    assert Slugifier.slugify("DATA Analyst") == "data-analyst"


def test_slugifier_replaces_spaces_with_hyphens() -> None:
    assert Slugifier.slugify("data analyst") == "data-analyst"


def test_slugifier_removes_unsafe_characters() -> None:
    assert Slugifier.slugify("Data Analyst @ R&D!") == "data-analyst-r-d"


def test_slugifier_collapses_repeated_hyphens() -> None:
    assert Slugifier.slugify("Data --- Analyst") == "data-analyst"


def test_slugifier_handles_french_accents_reasonably() -> None:
    assert Slugifier.slugify("Chargé d'études économiques") == "charge-d-etudes-economiques"
