from __future__ import annotations

from typing import Any


LATEX_REPLACEMENTS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
}


def escape_latex(value: str) -> str:
    escaped = value
    for source, target in LATEX_REPLACEMENTS.items():
        escaped = escaped.replace(source, target)
    return escaped


def escape_latex_data(value: Any, parent_key: str = "") -> Any:
    if isinstance(value, str):
        if parent_key in {"url", "url_label", "linkedin", "github", "portfolio", "email"}:
            return value
        return escape_latex(value)
    if isinstance(value, list):
        return [escape_latex_data(item, parent_key=parent_key) for item in value]
    if isinstance(value, dict):
        return {key: escape_latex_data(item, parent_key=key) for key, item in value.items()}
    return value
