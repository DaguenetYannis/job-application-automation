from __future__ import annotations

from src.models import JobInput, ParsedJob


class PromptBuilder:
    def build_cv_prompt(self, job_input: JobInput, parsed_job: ParsedJob, context: dict) -> str:
        raise NotImplementedError("CV prompt building is not implemented yet.")

    def build_cover_letter_prompt(self, job_input: JobInput, parsed_job: ParsedJob, context: dict) -> str:
        raise NotImplementedError("Cover letter prompt building is not implemented yet.")
