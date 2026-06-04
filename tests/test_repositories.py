import shutil
import uuid
from pathlib import Path

import pytest

from src.repositories import (
    ExampleRepository,
    ProfileRepository,
    RoleProfileRepository,
    SkillBlockRepository,
    TemplateRepository,
)


def isolated_dir(prefix: str) -> Path:
    path = Path(".test_artifacts") / f"{prefix}_{uuid.uuid4().hex}"
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_profile_repository_loads_candidate_profile() -> None:
    root = isolated_dir("profile")
    try:
        profile_path = root / "candidate_profile.yaml"
        profile_path.write_text("name: Test Candidate\nexperiences: []\n", encoding="utf-8")

        profile = ProfileRepository(profile_path).load()

        assert profile["name"] == "Test Candidate"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_profile_repository_raises_clear_error_for_invalid_yaml() -> None:
    root = isolated_dir("profile_invalid")
    try:
        profile_path = root / "candidate_profile.yaml"
        profile_path.write_text("name: [broken\n", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid YAML in candidate profile"):
            ProfileRepository(profile_path).load()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_role_profile_repository_loads_role_profiles() -> None:
    root = isolated_dir("roles")
    try:
        role_dir = root / "01_data_analyst"
        role_dir.mkdir()
        (role_dir / "profile.yaml").write_text(
            "category_id: 01_data_analyst\nlabel: Data Analyst\n",
            encoding="utf-8",
        )

        profiles = RoleProfileRepository(root).load_all()

        assert profiles["01_data_analyst"]["label"] == "Data Analyst"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_skill_block_repository_loads_french_skill_blocks() -> None:
    root = isolated_dir("skills")
    try:
        skill_dir = root / "fr"
        skill_dir.mkdir()
        (skill_dir / "sql.yaml").write_text(
            "skill_id: sql\nlabel: SQL\nlanguage: fr\n",
            encoding="utf-8",
        )

        blocks = SkillBlockRepository(root).load_language("fr")

        assert blocks["sql"]["label"] == "SQL"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_example_repository_lists_example_pdfs() -> None:
    root = isolated_dir("examples")
    try:
        folder = root / "cvs" / "01_data_analyst"
        folder.mkdir(parents=True)
        (folder / "example.pdf").write_text("pdf", encoding="utf-8")
        (folder / "README.md").write_text("readme", encoding="utf-8")

        examples = ExampleRepository(root).list_cv_examples("01_data_analyst")

        assert examples == [(folder / "example.pdf").as_posix()]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_template_repository_selects_french_and_english_templates() -> None:
    repository = TemplateRepository()

    assert repository.select_cv_template("fr") == "cv/cv_base_fr.tex.j2"
    assert repository.select_cv_template("unknown") == "cv/cv_base_fr.tex.j2"
    assert repository.select_cv_template("en") == "cv/cv_base_en.tex.j2"
    assert repository.select_cover_letter_template("en") == "cover_letter/cover_letter_base_en.tex.j2"
