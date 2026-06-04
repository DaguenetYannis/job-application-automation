from __future__ import annotations

import unicodedata
from typing import Any

from src.models import JobInput, ParsedJob
from src.repositories import (
    ExampleRepository,
    ProfileRepository,
    RoleProfileRepository,
    SkillBlockRepository,
    TemplateRepository,
)


class ContextSelector:
    def __init__(
        self,
        profile_repository: ProfileRepository | None = None,
        role_profile_repository: RoleProfileRepository | None = None,
        skill_block_repository: SkillBlockRepository | None = None,
        example_repository: ExampleRepository | None = None,
        template_repository: TemplateRepository | None = None,
    ) -> None:
        self.profile_repository = profile_repository or ProfileRepository()
        self.role_profile_repository = role_profile_repository or RoleProfileRepository()
        self.skill_block_repository = skill_block_repository or SkillBlockRepository()
        self.example_repository = example_repository or ExampleRepository()
        self.template_repository = template_repository or TemplateRepository()

    def select(self, job_input: JobInput, parsed_job: ParsedJob) -> dict[str, Any]:
        notes = ["Rule-based context selection, no API call."]
        candidate_profile = self._load_candidate_profile(notes)
        role_profiles = self.role_profile_repository.load_all()
        language = parsed_job.language if parsed_job.language in {"fr", "en"} else "fr"
        skill_blocks = self.skill_block_repository.load_language(language)

        selected_categories = (
            parsed_job.detected_role_categories
            or parsed_job.job_family
            or ["01_data_analyst"]
        )[:3]
        selected_profiles = [
            role_profiles[category_id]
            for category_id in selected_categories
            if category_id in role_profiles
        ]

        top_profile = selected_profiles[0] if selected_profiles else {}
        top_category = selected_categories[0] if selected_categories else "01_data_analyst"
        example_selection = top_profile.get("example_selection", {})
        max_cv_examples = int(example_selection.get("max_cv_examples", 2))
        max_cover_letter_examples = int(example_selection.get("max_cover_letter_examples", 2))

        selected_cv_examples = self.example_repository.list_cv_examples(top_category)[:max_cv_examples]
        selected_cover_letter_examples = self.example_repository.list_cover_letter_examples(top_category)[
            :max_cover_letter_examples
        ]
        selected_skill_ids = self._select_skill_ids(selected_profiles, skill_blocks, parsed_job)
        max_skill_blocks = int(top_profile.get("context_budget", {}).get("max_skill_blocks", 8))
        selected_skill_ids = selected_skill_ids[:max_skill_blocks]

        return {
            "language": language,
            "selected_role_categories": selected_categories,
            "selected_role_profiles": [self._compact_role_profile(profile) for profile in selected_profiles],
            "selected_cv_examples": selected_cv_examples,
            "selected_cover_letter_examples": selected_cover_letter_examples,
            "selected_skill_blocks": [
                self._compact_skill_block(skill_blocks[skill_id])
                for skill_id in selected_skill_ids
                if skill_id in skill_blocks
            ],
            "selected_templates": {
                "cv": self.template_repository.select_cv_template(language),
                "cover_letter": self.template_repository.select_cover_letter_template(language),
            },
            "selected_experiences": self._select_named_items(
                candidate_profile.get("experiences", []),
                self._preferred_values(selected_profiles, "preferred_experiences"),
                "organization",
            ),
            "selected_projects": self._select_named_items(
                candidate_profile.get("projects", []),
                self._preferred_values(selected_profiles, "preferred_projects"),
                "name",
            ),
            "notes": " ".join(notes),
        }

    def _load_candidate_profile(self, notes: list[str]) -> dict:
        try:
            return self.profile_repository.load()
        except ValueError as exc:
            notes.append(str(exc))
            return {}

    def _select_skill_ids(
        self,
        selected_profiles: list[dict],
        skill_blocks: dict[str, dict],
        parsed_job: ParsedJob,
    ) -> list[str]:
        selected: list[str] = []
        for skill_id in self._preferred_values(selected_profiles, "preferred_skills"):
            if skill_id in skill_blocks and skill_id not in selected:
                selected.append(skill_id)

        job_terms = parsed_job.detected_keywords + parsed_job.detected_required_skills + parsed_job.keywords
        normalized_job_terms = [self._normalize(term) for term in job_terms]
        for skill_id, block in skill_blocks.items():
            if skill_id in selected:
                continue
            block_terms = [skill_id, block.get("label", "")]
            block_terms.extend(block.get("keywords", []))
            normalized_block_terms = [self._normalize(term) for term in block_terms]
            if self._terms_overlap(normalized_job_terms, normalized_block_terms):
                selected.append(skill_id)
        return selected

    def _terms_overlap(self, job_terms: list[str], block_terms: list[str]) -> bool:
        for job_term in job_terms:
            for block_term in block_terms:
                if job_term and block_term and (job_term in block_term or block_term in job_term):
                    return True
        return False

    def _preferred_values(self, selected_profiles: list[dict], key: str) -> list[str]:
        values: list[str] = []
        for profile in selected_profiles:
            for value in profile.get(key, []):
                if value not in values:
                    values.append(value)
        return values

    def _select_named_items(
        self,
        items: list[dict],
        preferred_names: list[str],
        name_key: str,
    ) -> list[str]:
        if not items:
            return []

        selected: list[str] = []
        for preferred in preferred_names:
            preferred_normalized = self._normalize(preferred)
            for item in items:
                item_name = str(item.get(name_key, ""))
                if item_name and (
                    preferred_normalized in self._normalize(item_name)
                    or self._normalize(item_name) in preferred_normalized
                ):
                    if item_name not in selected:
                        selected.append(item_name)

        if selected:
            return selected[:3]

        return [str(item.get(name_key)) for item in items[:2] if item.get(name_key)]

    def _compact_role_profile(self, profile: dict) -> dict[str, Any]:
        return {
            "category_id": profile.get("category_id", ""),
            "label": profile.get("label", ""),
            "cv_angle": profile.get("cv_angle", ""),
            "cover_letter_angle": profile.get("cover_letter_angle", ""),
            "tone": profile.get("tone", []),
        }

    def _compact_skill_block(self, block: dict) -> dict[str, Any]:
        return {
            "skill_id": block.get("skill_id", ""),
            "label": block.get("label", ""),
            "short": block.get("short", ""),
            "medium": block.get("medium", ""),
            "keywords": block.get("keywords", []),
            "evidence": block.get("evidence", []),
        }

    def _normalize(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", str(text).lower())
        return normalized.encode("ascii", "ignore").decode("ascii")
