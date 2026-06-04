from __future__ import annotations

from pathlib import Path

from src.context_selector import ContextSelector
from src.generator import ApplicationGenerator
from src.models import ApplicationMetadata, JobInput
from src.parser import JobParser
from src.tracker import ApplicationTracker
from src.workspace import ApplicationWorkspace


class ApplicationPipeline:
    def __init__(
        self,
        applications_dir: Path = Path("applications"),
        tracker_path: Path = Path("tracker.csv"),
        generator: ApplicationGenerator | None = None,
    ) -> None:
        self.parser = JobParser()
        self.context_selector = ContextSelector()
        self.workspace = ApplicationWorkspace(applications_dir)
        self.tracker = ApplicationTracker(tracker_path)
        self.generator = generator or ApplicationGenerator()

    def run(self, job_input: JobInput) -> ApplicationMetadata:
        parsed_job = self.parser.parse(job_input.job_description)
        selected_context = self.context_selector.select(job_input, parsed_job)
        metadata = self.workspace.create(job_input, parsed_job, selected_context)
        self.tracker.append(metadata, parsed_job, status="context_selected")
        self.generator.generate(metadata, job_input, parsed_job, selected_context, self.tracker)
        return metadata
