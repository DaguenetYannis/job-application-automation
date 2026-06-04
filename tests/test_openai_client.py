from src.openai_client import OpenAIClient


def test_openai_client_returns_false_when_api_key_missing(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert OpenAIClient().is_configured() is False


def test_openai_client_returns_true_when_api_key_set(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    assert OpenAIClient().is_configured() is True
