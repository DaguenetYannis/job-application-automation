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
        document_strategy: dict,
        requirement_mapping: list[dict],
    ) -> str:
        company = job_input.company or ""
        raw_description = job_input.job_description[: self.MAX_JOB_DESCRIPTION_CHARS]
        parsed_job_json = json.dumps(asdict(parsed_job), ensure_ascii=False, indent=2)
        selected_context_json = json.dumps(selected_context, ensure_ascii=False, indent=2)
        document_strategy_json = json.dumps(document_strategy, ensure_ascii=False, indent=2)
        requirement_mapping_json = json.dumps(requirement_mapping, ensure_ascii=False, indent=2)

        return f"""
You generate structured job application content for a LaTeX rendering system.
Return only valid JSON. Do not include Markdown, commentary or code fences.
Do not invent facts. Use only the provided context and the job description.
Do not use the em dash character.
Write in the detected language: {parsed_job.language}.
Keep the CV concise and compatible with existing LaTeX templates.
Return plain text only inside JSON fields. Do not add LaTeX commands. The application will escape LaTeX-sensitive characters after generation.
Avoid unsupported claims. Keep Power BI, DAX and advanced BI claims proportional to the evidence.

Evidence preservation:
- Preserve concrete evidence from selected_context.
- Do not summarize away tools, datasets, methods or outputs.
- Use specific evidence when relevant.
- If a selected experience contains concrete tools, datasets or outputs, include them in bullets.
- Prefer factual bullets over generic statements.

No generic filler:
- Do not use these weak phrases unless immediately tied to concrete evidence:
  dynamic environment; strong quantitative approach; complex datasets; clear and usable outputs;
  closely aligned with my profile; make a significant impact; passionate about; excited to apply;
  proven track record.

CV density targets:
- 4 to 6 skill groups.
- 2 to 3 professional experiences when available.
- 4 to 6 bullets per main experience.
- 2 to 3 selected projects when relevant.
- Include all relevant education entries.
- Include all languages from candidate profile.
- Include tools, data types, methods and outputs in experience bullets.
- Keep the profile paragraph specific and not generic.

Cover letter targets:
- 4 paragraphs.
- Paragraph 1: role-specific motivation and positioning.
- Paragraph 2: evidence linked to main technical requirements.
- Paragraph 3: evidence linked to writing, research, reporting, stakeholder or domain requirements.
- Paragraph 4: concise closing.
- Mention the company or organization naturally.
- Include at least 2 concrete links between job requirements and candidate evidence.

Role-specific strategy:
- Follow document_strategy when deciding positioning, title, priorities and must_include_evidence.

Requirement mapping:
- Use requirement_mapping explicitly when deciding what to include in the CV and cover letter.

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

Document strategy:
{document_strategy_json}

Requirement mapping:
{requirement_mapping_json}
""".strip()

    def build_cv_prompt(self, job_input: JobInput, parsed_job: ParsedJob, context: dict) -> str:
        return self.build_application_prompt(job_input, parsed_job, context, {}, [])

    def build_cover_letter_prompt(self, job_input: JobInput, parsed_job: ParsedJob, context: dict) -> str:
        return self.build_application_prompt(job_input, parsed_job, context, {}, [])
