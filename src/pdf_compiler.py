from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from src.config import Config


class PDFCompiler:
    def __init__(self, compiler: str | None = None) -> None:
        self.compiler = compiler or Config.load_pdf_settings().compiler

    def compile(self, tex_path: Path, output_dir: Path, log_dir: Path) -> Path:
        if shutil.which(self.compiler) is None:
            raise RuntimeError(
                "LaTeX compiler not found. Install TeX Live or MiKTeX, or set PDF_COMPILER in .env."
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{tex_path.stem}_compile.log"
        command = [
            self.compiler,
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={output_dir.resolve()}",
            tex_path.name,
        ]

        result = subprocess.run(
            command,
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        log_path.write_text((result.stdout or "") + "\n" + (result.stderr or ""), encoding="utf-8")
        if result.returncode != 0:
            raise RuntimeError(f"LaTeX compilation failed for {tex_path}. See log: {log_path}")

        pdf_path = output_dir / f"{tex_path.stem}.pdf"
        if not pdf_path.exists():
            raise RuntimeError(f"LaTeX compiler finished but PDF was not found: {pdf_path}. See log: {log_path}")
        return pdf_path
