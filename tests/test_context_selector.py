import shutil
import uuid
from pathlib import Path

from src.context_selector import ContextSelector
from src.models import JobInput
from src.parser import JobParser
from src.repositories import ExampleRepository, ProfileRepository


def isolated_dir(prefix: str) -> Path:
    path = Path(".test_artifacts") / f"{prefix}_{uuid.uuid4().hex}"
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def make_selector(profile_path: Path, examples_dir: Path) -> ContextSelector:
    return ContextSelector(
        profile_repository=ProfileRepository(profile_path),
        example_repository=ExampleRepository(examples_dir),
    )


def write_profile(path: Path) -> None:
    path.write_text(
        """
experiences:
  - organization: Greenly
    role: Data Analyst
    keywords:
      - Python
      - SQL
      - carbon data
    achievements:
      - Used BigQuery and PostgreSQL for reporting.
  - organization: DataForGood / Reclaim Finance
    achievements:
      - Pipeline Python et DuckDB couvrant 43 annees de fiscal data.
projects:
  - name: Portfolio analytique
    keywords:
      - Reporting
  - name: Pipeline Machine Learning supervisé
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_context_selector_selects_bi_reporting_and_relevant_skills() -> None:
    root = isolated_dir("selector")
    try:
        profile_path = root / "candidate_profile.yaml"
        examples_dir = root / "examples"
        write_profile(profile_path)
        job_input = JobInput(
            job_title="BI Analyst",
            company=None,
            job_description="Nous cherchons Power BI, SQL, dashboards, KPI, reporting et Power Query.",
        )
        parsed = JobParser().parse(job_input.job_description)

        context = make_selector(profile_path, examples_dir).select(job_input, parsed)
        skill_ids = [block["skill_id"] for block in context["selected_skill_blocks"]]

        assert context["selected_role_categories"][0] == "02_bi_reporting_analytics"
        assert context["selected_templates"]["cv"] == "cv/cv_base_fr.tex.j2"
        assert "power_bi_reporting" in skill_ids
        assert "sql" in skill_ids
        assert "kpi_reporting" in skill_ids
        assert "Greenly" in context["selected_experiences"]
        assert "Portfolio analytique" in context["selected_projects"]
        assert context["selected_experience_details"]
        assert context["selected_project_details"]
        assert "evidence" in context["selected_experience_details"][0]
        assert "tools" in context["selected_experience_details"][0]["evidence"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_context_selector_selects_english_templates_for_english_jobs() -> None:
    root = isolated_dir("selector_en")
    try:
        profile_path = root / "candidate_profile.yaml"
        examples_dir = root / "examples"
        write_profile(profile_path)
        job_input = JobInput(
            job_title="Policy Analyst",
            company=None,
            job_description="We need a policy analyst. You will use SQL and Python for international reporting.",
        )
        parsed = JobParser().parse(job_input.job_description)

        context = make_selector(profile_path, examples_dir).select(job_input, parsed)

        assert context["selected_templates"]["cv"] == "cv/cv_base_en.tex.j2"
        assert context["selected_templates"]["cover_letter"] == "cover_letter/cover_letter_base_en.tex.j2"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_context_selector_does_not_crash_when_examples_are_empty() -> None:
    root = isolated_dir("selector_empty_examples")
    try:
        profile_path = root / "candidate_profile.yaml"
        examples_dir = root / "examples"
        write_profile(profile_path)
        job_input = JobInput(
            job_title="Data Analyst",
            company=None,
            job_description="Nous cherchons un Data Analyst SQL Python.",
        )
        parsed = JobParser().parse(job_input.job_description)

        context = make_selector(profile_path, examples_dir).select(job_input, parsed)

        assert context["selected_cv_examples"] == []
        assert context["selected_cover_letter_examples"] == []
        assert "no API call" in context["notes"]
    finally:
        shutil.rmtree(root, ignore_errors=True)
