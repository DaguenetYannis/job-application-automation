import csv
import json
import shutil
import uuid
from pathlib import Path

from src.generator import ApplicationGenerator
from src.models import JobInput
from src.openai_client import OpenAIClient
from src.pipeline import ApplicationPipeline


def isolated_dir() -> Path:
    path = Path(".test_artifacts") / f"pipeline_{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    return path


class FakeOpenAIClient(OpenAIClient):
    def __init__(self) -> None:
        pass

    def is_configured(self) -> bool:
        return True

    def generate_application_json(self, prompt: str) -> dict:
        return {
            "cv": {
                "title": "Data Analyst",
                "profile_paragraph": "Profile.",
                "skill_groups": [{"label": "Data", "content": "SQL, Python."}],
                "experiences": [
                    {
                        "organization": "Greenly",
                        "role": "Data Analyst",
                        "location": "Paris",
                        "dates": "2025",
                        "bullets": ["Analyzed data."],
                    }
                ],
                "projects": [],
                "education": [],
                "certifications": [],
                "languages": "French, English",
            },
            "cover_letter": {
                "date": "",
                "subject": "Candidature",
                "greeting": "Madame, Monsieur,",
                "paragraphs": ["First paragraph.", "Second paragraph."],
                "closing": "Cordialement,",
            },
        }


class FakePDFCompiler:
    def compile(self, tex_path: Path, output_dir: Path, log_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / f"{tex_path.stem}.pdf"
        pdf_path.write_text("pdf", encoding="utf-8")
        (log_dir / f"{tex_path.stem}_compile.log").write_text("ok", encoding="utf-8")
        return pdf_path


def test_pipeline_generation_writes_generated_outputs_and_pdf_status() -> None:
    root = isolated_dir()
    try:
        tracker_path = root / "tracker.csv"
        generator = ApplicationGenerator(
            openai_client=FakeOpenAIClient(),
            pdf_compiler=FakePDFCompiler(),
        )
        pipeline = ApplicationPipeline(
            applications_dir=root / "applications",
            tracker_path=tracker_path,
            generator=generator,
        )
        metadata = pipeline.run(
            JobInput(
                job_title="BI Analyst",
                company="Acme",
                job_description="Nous cherchons Power BI, SQL, dashboards, KPI, reporting et Power Query.",
            )
        )
        folder = Path(metadata.folder_path)

        assert (folder / "generated_content.json").exists()
        assert (folder / "document_strategy.json").exists()
        assert (folder / "requirement_mapping.json").exists()
        assert (folder / "logs" / "prompt.txt").exists()
        assert (folder / "quality_warnings.json").exists()
        assert (folder / "outputs" / "cv" / "cv.tex").exists()
        assert (folder / "outputs" / "cover_letter" / "cover_letter.tex").exists()
        assert (folder / "outputs" / "pdf" / "cv.pdf").exists()
        assert (folder / "outputs" / "pdf" / "cover_letter.pdf").exists()

        rows = list(csv.DictReader(tracker_path.open(newline="", encoding="utf-8")))
        assert rows[-1]["status"] == "pdf_generated"

        generated = json.loads((folder / "generated_content.json").read_text(encoding="utf-8"))
        assert generated["cv"]["title"] == "Data Analyst"
        warnings = json.loads((folder / "quality_warnings.json").read_text(encoding="utf-8"))
        assert warnings
    finally:
        shutil.rmtree(root, ignore_errors=True)
