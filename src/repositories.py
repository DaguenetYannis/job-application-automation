from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ProfileRepository:
    def __init__(self, profile_path: Path = Path("data/profile/candidate_profile.yaml")) -> None:
        self.profile_path = profile_path

    def load(self) -> dict:
        if not self.profile_path.exists():
            return {}
        return self._load_yaml(self.profile_path)

    def _load_yaml(self, path: Path) -> dict:
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in candidate profile: {path}") from exc
        return loaded or {}


class RoleProfileRepository:
    def __init__(self, role_profiles_dir: Path = Path("data/role_profiles")) -> None:
        self.role_profiles_dir = role_profiles_dir
        self._cache: dict[str, dict] | None = None

    def load_all(self) -> dict[str, dict]:
        profiles: dict[str, dict] = {}
        if not self.role_profiles_dir.exists():
            self._cache = profiles
            return profiles

        for path in sorted(self.role_profiles_dir.glob("*/profile.yaml")):
            profile = self._load_yaml(path)
            category_id = profile.get("category_id") or path.parent.name
            profile["category_id"] = category_id
            profiles[category_id] = profile

        self._cache = profiles
        return profiles

    def get(self, category_id: str) -> dict | None:
        profiles = self._cache if self._cache is not None else self.load_all()
        return profiles.get(category_id)

    def _load_yaml(self, path: Path) -> dict:
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in role profile: {path}") from exc
        return loaded or {}


class SkillBlockRepository:
    def __init__(self, skill_blocks_dir: Path = Path("data/skill_blocks")) -> None:
        self.skill_blocks_dir = skill_blocks_dir

    def load_language(self, language: str) -> dict[str, dict]:
        language_code = language if language in {"fr", "en"} else "fr"
        language_dir = self.skill_blocks_dir / language_code
        blocks: dict[str, dict] = {}
        if not language_dir.exists():
            return blocks

        for path in sorted(language_dir.glob("*.yaml")):
            block = self._load_yaml(path)
            skill_id = block.get("skill_id") or path.stem
            block["skill_id"] = skill_id
            blocks[skill_id] = block
        return blocks

    def load_all(self) -> dict[str, dict[str, dict]]:
        return {
            "fr": self.load_language("fr"),
            "en": self.load_language("en"),
        }

    def _load_yaml(self, path: Path) -> dict:
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in skill block: {path}") from exc
        return loaded or {}


class ExampleRepository:
    EXTENSIONS = {".pdf", ".tex", ".txt", ".md"}

    def __init__(self, examples_dir: Path = Path("data/examples")) -> None:
        self.examples_dir = examples_dir

    def list_cv_examples(self, category_id: str) -> list[str]:
        return self._list_examples(self.examples_dir / "cvs" / category_id)

    def list_cover_letter_examples(self, category_id: str) -> list[str]:
        return self._list_examples(self.examples_dir / "cover_letters" / category_id)

    def _list_examples(self, folder: Path) -> list[str]:
        if not folder.exists():
            return []
        paths = [
            path.as_posix()
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower() in self.EXTENSIONS
            and path.name.lower() != "readme.md"
        ]
        return sorted(paths)


class TemplateRepository:
    def __init__(self, templates_dir: Path = Path("data/templates")) -> None:
        self.templates_dir = templates_dir

    def select_cv_template(self, language: str) -> str:
        return "cv/cv_base_en.tex.j2" if language == "en" else "cv/cv_base_fr.tex.j2"

    def select_cover_letter_template(self, language: str) -> str:
        if language == "en":
            return "cover_letter/cover_letter_base_en.tex.j2"
        return "cover_letter/cover_letter_base_fr.tex.j2"
