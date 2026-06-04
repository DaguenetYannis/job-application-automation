import json
import shutil
import uuid
from pathlib import Path

from src.context_selector import ContextSelector
from src.models import JobInput, ParsedJob
from src.workspace import ApplicationWorkspace


def isolated_dir() -> Path:
    path = Path(".test_artifacts") / f"workspace_{uuid.uuid4().hex}"
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def make_job_input() -> JobInput:
    return JobInput(
        job_title="Data Analyst",
        company="Acme",
        job_description="We need a data analyst.",
    )


def make_parsed_job() -> ParsedJob:
    return ParsedJob(language="en")


def test_workspace_creates_application_folder_and_files() -> None:
    root = isolated_dir()
    try:
        workspace = ApplicationWorkspace(base_dir=root / "applications")
        job_input = make_job_input()
        parsed_job = make_parsed_job()
        context = ContextSelector().select(job_input, parsed_job)

        metadata = workspace.create(job_input, parsed_job, context)
        folder = Path(metadata.folder_path)

        assert folder.exists()
        assert (folder / "input.json").exists()
        assert (folder / "raw_job_description.txt").read_text(encoding="utf-8") == job_input.job_description
        assert (folder / "parsed_job.json").exists()
        assert (folder / "selected_context.json").exists()
        assert (folder / "generation_plan.json").exists()
        assert (folder / "outputs" / "cv").exists()
        assert (folder / "outputs" / "cover_letter").exists()
        assert (folder / "outputs" / "pdf").exists()
        assert (folder / "logs" / "run_log.txt").exists()

        input_data = json.loads((folder / "input.json").read_text(encoding="utf-8"))
        generation_plan = json.loads((folder / "generation_plan.json").read_text(encoding="utf-8"))
        assert input_data["job_title"] == "Data Analyst"
        assert generation_plan["status"] == "context_selected"
        assert "cv_template" in generation_plan
        assert generation_plan["selected_role_categories"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_workspace_does_not_overwrite_existing_folder_creates_suffix() -> None:
    root = isolated_dir()
    try:
        workspace = ApplicationWorkspace(base_dir=root / "applications")
        job_input = make_job_input()
        parsed_job = make_parsed_job()
        context = ContextSelector().select(job_input, parsed_job)

        first = workspace.create(job_input, parsed_job, context)
        second = workspace.create(job_input, parsed_job, context)

        assert first.folder_path != second.folder_path
        assert second.application_id.endswith("_2")
        assert (Path(first.folder_path) / "raw_job_description.txt").read_text(encoding="utf-8") == job_input.job_description
        assert (Path(second.folder_path) / "raw_job_description.txt").read_text(encoding="utf-8") == job_input.job_description
    finally:
        shutil.rmtree(root, ignore_errors=True)
