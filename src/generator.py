from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.document_strategy import DocumentStrategyBuilder
from src.latex_renderer import LatexRenderer
from src.latex_utils import escape_latex_data
from src.models import ApplicationMetadata, JobInput, ParsedJob
from src.openai_client import OpenAIClient
from src.output_validator import GeneratedContentValidator
from src.pdf_compiler import PDFCompiler
from src.progress import ProgressReporter
from src.prompt_builder import PromptBuilder
from src.requirement_mapper import RequirementMapper
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
        document_strategy_builder: DocumentStrategyBuilder | None = None,
        requirement_mapper: RequirementMapper | None = None,
        output_validator: GeneratedContentValidator | None = None,
    ) -> None:
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.openai_client = openai_client or OpenAIClient()
        self.latex_renderer = latex_renderer or LatexRenderer()
        self.pdf_compiler = pdf_compiler or PDFCompiler()
        self.profile_repository = profile_repository or ProfileRepository()
        self.document_strategy_builder = document_strategy_builder or DocumentStrategyBuilder()
        self.requirement_mapper = requirement_mapper or RequirementMapper()
        self.output_validator = output_validator or GeneratedContentValidator()

    def generate(
        self,
        metadata: ApplicationMetadata,
        job_input: JobInput,
        parsed_job: ParsedJob,
        selected_context: dict[str, Any],
        tracker: ApplicationTracker,
        progress: ProgressReporter | None = None,
    ) -> str:
        progress = progress or ProgressReporter()
        application_dir = Path(metadata.folder_path)
        logs_dir = application_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        api_log = logs_dir / "api_generation.log"
        progress.step(40, "Building document strategy")
        document_strategy = self.document_strategy_builder.build(job_input, parsed_job, selected_context)
        progress.step(45, "Mapping job requirements to candidate evidence")
        requirement_mapping = self.requirement_mapper.build_mapping(parsed_job, selected_context)
        progress.step(50, "Building OpenAI prompt")
        prompt = self.prompt_builder.build_application_prompt(
            job_input,
            parsed_job,
            selected_context,
            document_strategy,
            requirement_mapping,
        )
        progress.step(55, "Saving prompt and strategy files")
        self._write_json(application_dir / "document_strategy.json", document_strategy)
        self._write_json(application_dir / "requirement_mapping.json", requirement_mapping)
        (logs_dir / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")

        if not self.openai_client.is_configured():
            message = (
                "Application workspace created, but OpenAI generation was skipped because "
                "OPENAI_API_KEY is not configured."
            )
            api_log.write_text(message + "\n", encoding="utf-8")
            progress.step(60, "OpenAI generation skipped because OPENAI_API_KEY is not configured")
            print(message)
            tracker.update_status(metadata.application_id, "context_selected_no_api")
            progress.step(100, "Workspace and context files created")
            return "context_selected_no_api"

        progress.step(60, "Calling OpenAI for structured CV and cover letter content")
        api_log.write_text("Calling OpenAI for structured JSON content.\n", encoding="utf-8")
        generated = self.openai_client.generate_application_json(prompt)
        progress.step(70, "Saving generated content")
        self._write_json(application_dir / "generated_content.json", generated)
        tracker.update_status(metadata.application_id, "generated_json")

        progress.step(75, "Running quality checks")
        quality_warnings = self.output_validator.validate(generated, selected_context, document_strategy)
        self._write_json(application_dir / "quality_warnings.json", quality_warnings)
        if quality_warnings:
            progress.warning(f"{len(quality_warnings)} generation quality warning(s)")
            print("Generation quality warnings:")
            for warning in quality_warnings:
                progress.warning(warning)
                print(f"- {warning}")

        progress.step(80, "Rendering LaTeX files")
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
            progress.step(90, "Compiling PDFs")
            cv_pdf = self.pdf_compiler.compile(cv_tex_path, pdf_dir, logs_dir)
            cover_letter_pdf = self.pdf_compiler.compile(cover_letter_tex_path, pdf_dir, logs_dir)
        except RuntimeError as exc:
            tracker.update_status(metadata.application_id, "latex_failed")
            progress.error("LaTeX compilation failed. See logs in the application folder.")
            print(str(exc))
            progress.step(100, "Generated LaTeX files kept for debugging")
            return "latex_failed"

        tracker.update_status(metadata.application_id, "pdf_generated")
        progress.step(100, "Application packet generated")
        print(f"CV LaTeX: {cv_tex_path}")
        print(f"Cover letter LaTeX: {cover_letter_tex_path}")
        print(f"CV PDF: {cv_pdf}")
        print(f"Cover letter PDF: {cover_letter_pdf}")
        return "pdf_generated"

    def _write_json(self, path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

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
