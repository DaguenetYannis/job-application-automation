from __future__ import annotations

from typing import Any

from src.models import JobInput, ParsedJob
from src.role_categories import ROLE_CATEGORIES


class ContextSelector:
    def select(self, job_input: JobInput, parsed_job: ParsedJob) -> dict[str, Any]:
        return {
            "cv_examples": [],
            "cover_letter_examples": [],
            "skill_blocks": [],
            "templates": [],
            "role_categories": [category.slug for category in ROLE_CATEGORIES],
            "notes": "Context selection not implemented yet.",
        }
