from src.progress import ProgressReporter


def test_progress_step_prints_percent_and_label(capsys) -> None:
    ProgressReporter(enabled=True).step(10, "Parsing job description")

    captured = capsys.readouterr()
    assert "[ 10%]" in captured.out
    assert "Parsing job description" in captured.out


def test_progress_disabled_prints_nothing(capsys) -> None:
    ProgressReporter(enabled=False).step(10, "Parsing job description")

    captured = capsys.readouterr()
    assert captured.out == ""


def test_progress_warning_prints_warn(capsys) -> None:
    ProgressReporter(enabled=True).warning("Quality warning")

    captured = capsys.readouterr()
    assert "[WARN]" in captured.out
    assert "Quality warning" in captured.out


def test_progress_error_prints_err(capsys) -> None:
    ProgressReporter(enabled=True).error("Compilation failed")

    captured = capsys.readouterr()
    assert "[ERR ]" in captured.out
    assert "Compilation failed" in captured.out
