from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.latex_renderer import LatexRenderer
from src.latex_utils import escape_latex_data
from src.models import ApplicationMetadata, JobInput, ParsedJob
from src.openai_client import OpenAIClient
from src.pdf_compiler import PDFCompiler
from src.prompt_builder import PromptBuilder
from src.repositories import ProfileRepository
from src.tracker import ApplicationTracker


class ApplicationGenerator:
    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        openai_client: OpenAIClient | None = None,
        latex_renderer: LatexRenderer | None = None,
        pdf_compiler: PDFCompiler | None = None,
        profile_repository: ProfileRepository | None = None,
    ) -> None:
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.openai_client = openai_client or OpenAIClient()
        self.latex_renderer = latex_renderer or LatexRenderer()
        self.pdf_compiler = pdf_compiler or PDFCompiler()
        self.profile_repository = profile_repository or ProfileRepository()

    def generate(
        self,
        metadata: ApplicationMetadata,
        job_input: JobInput,
        parsed_job: ParsedJob,
        selected_context: dict[str, Any],
        tracker: ApplicationTracker,
    ) -> str:
        application_dir = Path(metadata.folder_path)
        logs_dir = application_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        api_log = logs_dir / "api_generation.log"

        if not self.openai_client.is_configured():
            message = (
                "Application workspace created, but OpenAI generation was skipped because "
                "OPENAI_API_KEY is not configured."
            )
            api_log.write_text(message + "\n", encoding="utf-8")
            print(message)
            tracker.update_status(metadata.application_id, "context_selected_no_api")
            return "context_selected_no_api"

        prompt = self.prompt_builder.build_application_prompt(job_input, parsed_job, selected_context)
        api_log.write_text("Calling OpenAI for structured JSON content.\n", encoding="utf-8")
        generated = self.openai_client.generate_application_json(prompt)
        (application_dir / "generated_content.json").write_text(
            json.dumps(generated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        tracker.update_status(metadata.application_id, "generated_json")

        escaped_generated = escape_latex_data(generated)
        candidate_identity = self._candidate_identity()
        cv_tex_path = application_dir / "outputs" / "cv" / "cv.tex"
        cover_letter_tex_path = application_dir / "outputs" / "cover_letter" / "cover_letter.tex"
        pdf_dir = application_dir / "outputs" / "pdf"

        cv_tex = self.latex_renderer.render(
            selected_context["selected_templates"]["cv"],
            self._cv_render_context(candidate_identity, escaped_generated),
        )
        cover_letter_tex = self.latex_renderer.render(
            selected_context["selected_templates"]["cover_letter"],
            self._cover_letter_render_context(candidate_identity, job_input, escaped_generated),
        )
        cv_tex_path.write_text(cv_tex, encoding="utf-8")
        cover_letter_tex_path.write_text(cover_letter_tex, encoding="utf-8")
        tracker.update_status(metadata.application_id, "latex_rendered")

        try:
            cv_pdf = self.pdf_compiler.compile(cv_tex_path, pdf_dir, logs_dir)
            cover_letter_pdf = self.pdf_compiler.compile(cover_letter_tex_path, pdf_dir, logs_dir)
        except RuntimeError as exc:
            tracker.update_status(metadata.application_id, "latex_failed")
            print(str(exc))
            return "latex_failed"

        tracker.update_status(metadata.application_id, "pdf_generated")
        print(f"CV LaTeX: {cv_tex_path}")
        print(f"Cover letter LaTeX: {cover_letter_tex_path}")
        print(f"CV PDF: {cv_pdf}")
        print(f"Cover letter PDF: {cover_letter_pdf}")
        return "pdf_generated"

    def _candidate_identity(self) -> dict[str, str]:
        profile = self.profile_repository.load()
        return {
            "name": str(profile.get("name", "")),
            "email": str(profile.get("email", "")),
            "phone": str(profile.get("phone", "")),
            "location": str(profile.get("location", "")),
            "linkedin": str(profile.get("linkedin", "")),
            "github": str(profile.get("github", "")),
            "portfolio": str(profile.get("portfolio", "")),
        }

    def _cv_render_context(self, candidate_identity: dict[str, str], generated: dict[str, Any]) -> dict[str, Any]:
        cv = generated.get("cv", {})
        return {
            "layout": {"margin": "1.75cm", "line_stretch": "1.04"},
            "candidate": candidate_identity,
            "document": {"title": cv.get("title", "")},
            "profile_paragraph": cv.get("profile_paragraph", ""),
            "skill_groups": cv.get("skill_groups", []),
            "experiences": cv.get("experiences", []),
            "projects": cv.get("projects", []),
            "education": cv.get("education", []),
            "certifications": cv.get("certifications", []),
            "languages": cv.get("languages", ""),
        }

    def _cover_letter_render_context(
        self,
        candidate_identity: dict[str, str],
        job_input: JobInput,
        generated: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "layout": {"margin": "1.9cm", "line_stretch": "1.05"},
            "candidate": candidate_identity,
            "recipient": {"name": "", "organization": job_input.company or "", "address": ""},
            "letter": generated.get("cover_letter", {}),
        }
