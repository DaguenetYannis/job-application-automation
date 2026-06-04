from __future__ import annotations

import json
import os

from src.config import Config, OpenAISettings


class OpenAIClient:
    def __init__(
        self,
        load_environment: bool = True,
        settings: OpenAISettings | None = None,
        client: object | None = None,
    ) -> None:
        self.settings = settings or (
            Config.load_openai_settings()
            if load_environment
            else OpenAISettings(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
                max_output_tokens=int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "8000")),
            )
        )
        self.api_key = self.settings.api_key
        self.client = client

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_application_json(self, prompt: str) -> dict:
        if not self.is_configured():
            raise RuntimeError("OPENAI_API_KEY is not configured. Add it to your environment or .env file.")
        if self.client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError("OpenAI SDK is not installed. Run pip install -r requirements.txt.") from exc
            self.client = OpenAI(api_key=self.api_key)

        text = self._call_model(prompt)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"OpenAI response was not valid JSON. Raw response: {text}") from exc
        if not isinstance(parsed, dict):
            raise RuntimeError(f"OpenAI response JSON must be an object. Raw response: {text}")
        return parsed

    def _call_model(self, prompt: str) -> str:
        if hasattr(self.client, "responses"):
            response = self.client.responses.create(
                model=self.settings.model,
                input=prompt,
                max_output_tokens=self.settings.max_output_tokens,
            )
            return response.output_text

        response = self.client.chat.completions.create(
            model=self.settings.model,
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.settings.max_output_tokens,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""

    def generate_cv_latex(self) -> str:
        raise NotImplementedError("Raw LaTeX generation is not used. Generate structured JSON instead.")

    def generate_cover_letter_latex(self) -> str:
        raise NotImplementedError("Raw LaTeX generation is not used. Generate structured JSON instead.")
