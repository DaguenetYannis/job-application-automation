from __future__ import annotations

import os

from dotenv import load_dotenv


class OpenAIClient:
    def __init__(self) -> None:
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_cv_latex(self) -> str:
        # TODO: Use the OpenAI API to generate tailored CV LaTeX.
        raise NotImplementedError("CV generation is not implemented yet.")

    def generate_cover_letter_latex(self) -> str:
        # TODO: Use the OpenAI API to generate tailored cover letter LaTeX.
        raise NotImplementedError("Cover letter generation is not implemented yet.")
