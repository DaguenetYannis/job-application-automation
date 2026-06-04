import csv
import shutil
import uuid
from pathlib import Path

from src.models import ApplicationMetadata, ParsedJob
from src.tracker import ApplicationTracker


def isolated_dir() -> Path:
    path = Path(".test_artifacts") / f"tracker_{uuid.uuid4().hex}"
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def make_metadata(application_id: str) -> ApplicationMetadata:
    return ApplicationMetadata(
        application_id=application_id,
        job_title="Data Analyst",
        company="Acme",
        created_at="2026-06-04T12:00:00",
        folder_path=f"applications/{application_id}",
    )


def test_tracker_creates_tracker_csv_if_missing() -> None:
    root = isolated_dir()
    tracker_path = root / "tracker.csv"
    try:
        ApplicationTracker(tracker_path).append(make_metadata("app-1"), ParsedJob(language="en"))

        assert tracker_path.exists()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_tracker_appends_one_row() -> None:
    root = isolated_dir()
    tracker_path = root / "tracker.csv"
    try:
        ApplicationTracker(tracker_path).append(make_metadata("app-1"), ParsedJob(language="en"))

        rows = list(csv.DictReader(tracker_path.open(newline="", encoding="utf-8")))
        assert len(rows) == 1
        assert rows[0]["application_id"] == "app-1"
        assert rows[0]["status"] == "created"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_tracker_preserves_existing_rows() -> None:
    root = isolated_dir()
    tracker_path = root / "tracker.csv"
    try:
        tracker = ApplicationTracker(tracker_path)

        tracker.append(make_metadata("app-1"), ParsedJob(language="en"))
        tracker.append(make_metadata("app-2"), ParsedJob(language="fr"))

        rows = list(csv.DictReader(tracker_path.open(newline="", encoding="utf-8")))
        assert [row["application_id"] for row in rows] == ["app-1", "app-2"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_tracker_writes_correct_headers() -> None:
    root = isolated_dir()
    tracker_path = root / "tracker.csv"
    try:
        ApplicationTracker(tracker_path).append(make_metadata("app-1"), ParsedJob(language="en"))

        with tracker_path.open(newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)

        assert headers == [
            "application_id",
            "created_at",
            "job_title",
            "company",
            "language",
            "status",
            "folder_path",
        ]
    finally:
        shutil.rmtree(root, ignore_errors=True)
