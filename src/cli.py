from __future__ import annotations

import sys

from src.models import JobInput
from src.pipeline import ApplicationPipeline


class JobApplicationCLI:
    def new(self) -> None:
        job_title = input("Job title: ")
        company = input("Company (optional): ")
        print("Paste the job description, then press Ctrl+Z and Enter on Windows or Ctrl+D on macOS/Linux:")
        job_description = sys.stdin.read()

        job_input = JobInput(
            job_title=job_title,
            company=company,
            job_description=job_description,
        )
        metadata = ApplicationPipeline().run(job_input)

        print(f"Created application folder: {metadata.folder_path}")
        print("Tracker updated: tracker.csv")
