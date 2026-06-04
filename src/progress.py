from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProgressStep:
    percent: int
    label: str


class ProgressReporter:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def step(self, percent: int, label: str) -> None:
        if not self.enabled:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{percent:>3}%] {timestamp} | {label}")

    def info(self, label: str) -> None:
        if not self.enabled:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"      {timestamp} | {label}")

    def warning(self, label: str) -> None:
        if not self.enabled:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[WARN] {timestamp} | {label}")

    def error(self, label: str) -> None:
        if not self.enabled:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[ERR ] {timestamp} | {label}")
