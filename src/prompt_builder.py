from __future__ import annotations

import json
from dataclasses import asdict

from src.models import JobInput, ParsedJob


class PromptBuilder:
    MAX_JOB_DESCRIPTION_CHARS = 12000

    def build_application_prompt(
        self,
        job_input: JobInput,
        parsed_job: ParsedJob,
        selected_context: dict,
    ) -> str:
        company = job_input.company or ""
        raw_description = job_input.job_description[: self.MAX_JOB_DESCRIPTION_CHARS]
        parsed_job_json = json.dumps(asdict(parsed_job), ensure_ascii=False, indent=2)
        selected_context_json = json.dumps(selected_context, ensure_ascii=False, indent=2)

        return f"""
You generate structured job application content for a LaTeX rendering system.
Return only valid JSON. Do not include Markdown, commentary or code fences.
Do not invent facts. Use only the provided context and the job description.
Do not use the em dash character.
Write in the detected language: {parsed_job.language}.
Keep the CV concise and compatible with existing LaTeX templates.
Escape LaTeX-sensitive characters in generated text where needed: &, %, _, # and $.
Avoid unsupported claims. Keep Power BI, DAX and advanced BI claims proportional to the evidence.

Return exactly this JSON structure:
{{
  "cv": {{
    "title": "",
    "profile_paragraph": "",
    "skill_groups": [
      {{"label": "", "content": ""}}
    ],
    "experiences": [
      {{
        "organization": "",
        "role": "",
        "location": "",
        "dates": "",
        "bullets": []
      }}
    ],
    "projects": [
      {{
        "name": "",
        "year": "",
        "bullets": [],
        "url": "",
        "url_label": ""
      }}
    ],
    "education": [
      {{
        "institution": "",
        "dates": "",
        "degree": "",
        "details": ""
      }}
    ],
    "certifications": [
      {{
        "provider": "",
        "name": "",
        "year": ""
      }}
    ],
    "languages": ""
  }},
  "cover_letter": {{
    "date": "",
    "subject": "",
    "greeting": "",
    "paragraphs": [],
    "closing": ""
  }}
}}

Job title: {job_input.job_title}
Company: {company}

Raw job description:
{raw_description}

Parsed job:
{parsed_job_json}

Selected context:
{selected_context_json}
""".strip()

    def build_cv_prompt(self, job_input: JobInput, parsed_job: ParsedJob, context: dict) -> str:
        return self.build_application_prompt(job_input, parsed_job, context)

    def build_cover_letter_prompt(self, job_input: JobInput, parsed_job: ParsedJob, context: dict) -> str:
        return self.build_application_prompt(job_input, parsed_job, context)
