from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    applications_dir: Path = Path("applications")
    tracker_path: Path = Path("tracker.csv")
