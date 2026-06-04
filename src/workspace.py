from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models import ApplicationMetadata, JobInput, ParsedJob
from src.slugifier import Slugifier


class ApplicationWorkspace:
    def __init__(self, base_dir: Path = Path("applications")) -> None:
        self.base_dir = base_dir

    def create(
        self,
        job_input: JobInput,
        parsed_job: ParsedJob,
        selected_context: dict[str, Any],
    ) -> ApplicationMetadata:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now().replace(microsecond=0).isoformat()
        folder = self._unique_folder(job_input)
        folder.mkdir(parents=True)

        metadata = ApplicationMetadata(
            application_id=folder.name,
            job_title=job_input.job_title,
            company=job_input.company,
            created_at=created_at,
            folder_path=folder.as_posix(),
        )

        self._write_json(folder / "input.json", asdict(job_input))
        self._write_text_exclusive(folder / "raw_job_description.txt", job_input.job_description)
        self._write_json(folder / "parsed_job.json", asdict(parsed_job))
        self._write_json(folder / "selected_context.json", selected_context)
        self._write_json(folder / "generation_plan.json", self._generation_plan(parsed_job, selected_context))
        self._create_output_dirs(folder)
        self._write_text_exclusive(folder / "logs" / "run_log.txt", f"Created {created_at}\n")

        return metadata

    def _unique_folder(self, job_input: JobInput) -> Path:
        date_prefix = datetime.now().strftime("%Y-%m-%d")
        company_slug = Slugifier.slugify(job_input.company or "unknown")
        title_slug = Slugifier.slugify(job_input.job_title)
        base_name = f"{date_prefix}_{company_slug}_{title_slug}"
        candidate = self.base_dir / base_name
        counter = 2

        while candidate.exists():
            candidate = self.base_dir / f"{base_name}_{counter}"
            counter += 1

        return candidate

    def _create_output_dirs(self, folder: Path) -> None:
        for path in [
            folder / "outputs" / "cv",
            folder / "outputs" / "cover_letter",
            folder / "outputs" / "pdf",
            folder / "logs",
        ]:
            path.mkdir(parents=True, exist_ok=True)
            if path.name != "logs":
                (path / ".gitkeep").touch()

    def _write_json(self, path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _write_text_exclusive(self, path: Path, text: str) -> None:
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _generation_plan(self, parsed_job: ParsedJob, selected_context: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "context_selected",
            "language": parsed_job.language,
            "selected_role_categories": selected_context.get("selected_role_categories", []),
            "cv_template": selected_context.get("selected_templates", {}).get("cv", ""),
            "cover_letter_template": selected_context.get("selected_templates", {}).get("cover_letter", ""),
            "selected_cv_examples": selected_context.get("selected_cv_examples", []),
            "selected_cover_letter_examples": selected_context.get("selected_cover_letter_examples", []),
            "selected_skill_blocks": [
                block.get("skill_id", "")
                for block in selected_context.get("selected_skill_blocks", [])
                if block.get("skill_id")
            ],
            "selected_experiences": selected_context.get("selected_experiences", []),
            "selected_projects": selected_context.get("selected_projects", []),
            "next_steps": [
                "build_prompts",
                "generate_structured_cv_content",
                "generate_structured_cover_letter_content",
                "render_latex",
                "compile_pdfs",
            ],
            "notes": "No API call has been made.",
        }
