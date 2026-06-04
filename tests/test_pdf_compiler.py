import shutil
import uuid
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.pdf_compiler import PDFCompiler


def isolated_dir() -> Path:
    path = Path(".test_artifacts") / f"pdf_{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    return path


def test_pdf_compiler_builds_command_and_writes_logs(monkeypatch) -> None:
    root = isolated_dir()
    try:
        tex_path = root / "cv.tex"
        tex_path.write_text("\\documentclass{article}\\begin{document}x\\end{document}", encoding="utf-8")
        output_dir = root / "pdf"
        log_dir = root / "logs"

        monkeypatch.setattr("src.pdf_compiler.shutil.which", lambda compiler: "xelatex")

        def fake_run(command, cwd, capture_output, text, check):
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "cv.pdf").write_text("pdf", encoding="utf-8")
            fake_run.command = command
            return type("Result", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()

        monkeypatch.setattr("src.pdf_compiler.subprocess.run", fake_run)

        pdf_path = PDFCompiler("xelatex").compile(tex_path, output_dir, log_dir)

        assert "-interaction=nonstopmode" in fake_run.command
        assert "-halt-on-error" in fake_run.command
        assert (log_dir / "cv_compile.log").exists()
        assert pdf_path == output_dir / "cv.pdf"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_pdf_compiler_missing_compiler_raises_clear_error(monkeypatch) -> None:
    root = isolated_dir()
    try:
        tex_path = root / "cv.tex"
        tex_path.write_text("x", encoding="utf-8")
        monkeypatch.setattr("src.pdf_compiler.shutil.which", lambda compiler: None)

        with pytest.raises(RuntimeError, match="LaTeX compiler not found"):
            PDFCompiler("missing").compile(tex_path, root / "pdf", root / "logs")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_pdf_compiler_failure_points_to_log(monkeypatch) -> None:
    root = isolated_dir()
    try:
        tex_path = root / "cover_letter.tex"
        tex_path.write_text("x", encoding="utf-8")
        monkeypatch.setattr("src.pdf_compiler.shutil.which", lambda compiler: "xelatex")
        monkeypatch.setattr(
            "src.pdf_compiler.subprocess.run",
            Mock(return_value=type("Result", (), {"returncode": 1, "stdout": "bad", "stderr": "error"})()),
        )

        with pytest.raises(RuntimeError, match="cover_letter_compile.log"):
            PDFCompiler("xelatex").compile(tex_path, root / "pdf", root / "logs")
    finally:
        shutil.rmtree(root, ignore_errors=True)
