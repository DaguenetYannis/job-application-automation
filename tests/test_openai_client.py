import pytest

from src.config import OpenAISettings
from src.openai_client import OpenAIClient


def test_openai_client_returns_false_when_api_key_missing(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert OpenAIClient(load_environment=False).is_configured() is False


def test_openai_client_returns_true_when_api_key_set(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    assert OpenAIClient(load_environment=False).is_configured() is True


def test_openai_generation_raises_clear_error_without_api_key() -> None:
    client = OpenAIClient(load_environment=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not configured"):
        client.generate_application_json("prompt")


class FakeResponses:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text

    def create(self, **kwargs):
        return type("Response", (), {"output_text": self.output_text})()


class FakeClient:
    def __init__(self, output_text: str) -> None:
        self.responses = FakeResponses(output_text)


def test_openai_generation_parses_json_response() -> None:
    client = OpenAIClient(
        settings=OpenAISettings(api_key="test-key", model="test-model", max_output_tokens=100),
        client=FakeClient('{"cv": {}, "cover_letter": {}}'),
    )

    assert client.generate_application_json("prompt") == {"cv": {}, "cover_letter": {}}


def test_openai_generation_invalid_json_raises_clear_error() -> None:
    client = OpenAIClient(
        settings=OpenAISettings(api_key="test-key", model="test-model", max_output_tokens=100),
        client=FakeClient("not json"),
    )

    with pytest.raises(RuntimeError, match="OpenAI response was not valid JSON"):
        client.generate_application_json("prompt")
