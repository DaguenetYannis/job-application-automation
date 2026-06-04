from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

class LatexRenderer:
    def __init__(self, template_root: Path = Path("data/templates")) -> None:
        self.template_root = template_root
        self.environment = Environment(
            loader=FileSystemLoader(self.template_root),
            block_start_string="((*",
            block_end_string="*))",
            variable_start_string="(((",
            variable_end_string=")))",
            comment_start_string="((#",
            comment_end_string="#))",
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_path: str, context: dict[str, Any]) -> str:
        template = self.environment.get_template(template_path)
        return template.render(**context)
