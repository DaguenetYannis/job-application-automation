from __future__ import annotations

from pathlib import Path

from src.context_selector import ContextSelector
from src.generator import ApplicationGenerator
from src.models import ApplicationMetadata, JobInput
from src.parser import JobParser
from src.progress import ProgressReporter
from src.tracker import ApplicationTracker
from src.workspace import ApplicationWorkspace


class ApplicationPipeline:
    def __init__(
        self,
        applications_dir: Path = Path("applications"),
        tracker_path: Path = Path("tracker.csv"),
        generator: ApplicationGenerator | None = None,
        progress: ProgressReporter | None = None,
    ) -> None:
        self.parser = JobParser()
        self.context_selector = ContextSelector()
        self.workspace = ApplicationWorkspace(applications_dir)
        self.tracker = ApplicationTracker(tracker_path)
        self.generator = generator or ApplicationGenerator()
        self.progress = progress or ProgressReporter()

    def run(self, job_input: JobInput) -> ApplicationMetadata:
        self.progress.step(5, "Validating input")
        self.progress.step(10, "Parsing job description")
        parsed_job = self.parser.parse(job_input.job_description)
        self.progress.step(20, "Selecting local context")
        selected_context = self.context_selector.select(job_input, parsed_job)
        self.progress.step(30, "Creating application workspace")
        metadata = self.workspace.create(job_input, parsed_job, selected_context)
        self.tracker.append(metadata, parsed_job, status="context_selected")
        self.generator.generate(
            metadata,
            job_input,
            parsed_job,
            selected_context,
            self.tracker,
            progress=self.progress,
        )
        return metadata
