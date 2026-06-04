from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    applications_dir: Path = Path("applications")
    tracker_path: Path = Path("tracker.csv")


@dataclass(frozen=True)
class OpenAISettings:
    api_key: str | None
    model: str
    max_output_tokens: int


@dataclass(frozen=True)
class PDFSettings:
    compiler: str


class Config:
    @staticmethod
    def load_openai_settings() -> OpenAISettings:
        load_dotenv()
        return OpenAISettings(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            max_output_tokens=int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "8000")),
        )

    @staticmethod
    def load_pdf_settings() -> PDFSettings:
        load_dotenv()
        return PDFSettings(
            compiler=os.getenv("PDF_COMPILER", "xelatex"),
        )
