from src.output_validator import GeneratedContentValidator


def selected_context() -> dict:
    return {
        "selected_experiences": ["Greenly", "DataForGood / Reclaim Finance"],
        "candidate_languages": [
            {"language": "French", "level": "Native"},
            {"language": "English", "level": "C2"},
        ],
        "selected_experience_details": [
            {
                "organization": "Greenly",
                "evidence": {
                    "tools": ["Python", "SQL"],
                    "datasets": ["carbon data"],
                    "methods": ["ETL"],
                    "outputs": ["reporting"],
                    "domain": ["GHG Protocol"],
                },
            }
        ],
        "selected_project_details": [],
        "selected_skill_blocks": [],
    }


def strategy() -> dict:
    return {
        "must_include_evidence": ["Python", "carbon data"],
        "quality_targets": {"min_skill_groups": 4, "min_experience_bullets": 4},
        "source_summary": {"company": "Acme"},
    }


def weak_generated() -> dict:
    return {
        "cv": {
            "skill_groups": [{"label": "Data", "content": "Analysis"}],
            "experiences": [{"organization": "Greenly", "bullets": ["Worked with data."]}],
            "education": [],
            "languages": "English",
        },
        "cover_letter": {"paragraphs": ["I am excited to apply.", "Second."]},
    }


def good_generated() -> dict:
    return {
        "cv": {
            "skill_groups": [
                {"label": "SQL", "content": "SQL, Python, BigQuery."},
                {"label": "Carbon data", "content": "carbon data, GHG Protocol."},
                {"label": "Pipelines", "content": "ETL and quality checks."},
                {"label": "Reporting", "content": "client reporting."},
            ],
            "experiences": [
                {
                    "organization": "Greenly",
                    "bullets": [
                        "Used Python and SQL on carbon data.",
                        "Built ETL checks.",
                        "Prepared reporting.",
                        "Documented GHG Protocol work.",
                    ],
                },
                {"organization": "DataForGood / Reclaim Finance", "bullets": ["Built DuckDB pipeline."] * 4},
            ],
            "education": [{"institution": "Dauphine"}],
            "languages": "French, English",
        },
        "cover_letter": {
            "paragraphs": [
                "Acme role positioning.",
                "Python and carbon data evidence.",
                "Reporting evidence.",
                "Closing.",
            ]
        },
    }


def test_warns_when_cv_has_too_few_skill_groups() -> None:
    warnings = GeneratedContentValidator().validate(weak_generated(), selected_context(), strategy())
    assert any("fewer than 4 skill groups" in warning for warning in warnings)


def test_warns_when_experience_bullets_are_too_short() -> None:
    warnings = GeneratedContentValidator().validate(weak_generated(), selected_context(), strategy())
    assert any("Main experience has fewer than 4 bullets" in warning for warning in warnings)


def test_warns_when_languages_are_missing() -> None:
    generated = weak_generated()
    generated["cv"]["languages"] = ""
    warnings = GeneratedContentValidator().validate(generated, selected_context(), strategy())
    assert any("Languages are missing" in warning for warning in warnings)


def test_warns_when_cover_letter_has_fewer_than_4_paragraphs() -> None:
    warnings = GeneratedContentValidator().validate(weak_generated(), selected_context(), strategy())
    assert any("Cover letter has fewer than 4 paragraphs" in warning for warning in warnings)


def test_warns_when_generic_phrases_appear() -> None:
    warnings = GeneratedContentValidator().validate(weak_generated(), selected_context(), strategy())
    assert any("generic phrase" in warning for warning in warnings)


def test_returns_no_critical_warning_for_good_generated_object() -> None:
    warnings = GeneratedContentValidator().validate(good_generated(), selected_context(), strategy())
    assert warnings == []
