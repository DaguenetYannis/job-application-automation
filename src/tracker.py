from __future__ import annotations

import csv
from pathlib import Path

from src.models import ApplicationMetadata, ParsedJob


class ApplicationTracker:
    HEADERS = [
        "application_id",
        "created_at",
        "job_title",
        "company",
        "language",
        "status",
        "folder_path",
    ]

    def __init__(self, tracker_path: Path = Path("tracker.csv")) -> None:
        self.tracker_path = tracker_path

    def append(self, metadata: ApplicationMetadata, parsed_job: ParsedJob) -> None:
        self.tracker_path.parent.mkdir(parents=True, exist_ok=True)
        needs_header = not self.tracker_path.exists() or self.tracker_path.stat().st_size == 0

        with self.tracker_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.HEADERS)
            if needs_header:
                writer.writeheader()
            writer.writerow(
                {
                    "application_id": metadata.application_id,
                    "created_at": metadata.created_at,
                    "job_title": metadata.job_title,
                    "company": metadata.company or "",
                    "language": parsed_job.language,
                    "status": "created",
                    "folder_path": metadata.folder_path,
                }
            )
