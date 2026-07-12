import pytest

from ai_commit import CLIArgs
import ai_commit.providers as providers


@pytest.fixture
def use_remote(monkeypatch):
    """Points ai_commit.providers.args at a remote CLIArgs instance so
    get_ai_provider() takes the remote-provider code path."""
    monkeypatch.setattr(
        providers, "args", CLIArgs(remote=True, debug=False, model=None)
    )


def test_unknown_provider_exits_cleanly_instead_of_crashing(
    use_remote, monkeypatch, capsys
):
    # Before the fix, an unrecognized AI_COMMIT_PROVIDER value made
    # providers_mapping.get() return None, and the next line accessed
    # `.model` on it, raising an unhandled AttributeError.
    monkeypatch.setenv("AI_COMMIT_PROVIDER", "totally-not-a-real-provider")
    with pytest.raises(SystemExit):
        providers.get_ai_provider()
    assert "Unknown provider" in capsys.readouterr().out


def test_openai_provider_base_url_is_none_not_empty_string():
    # Regression test: base_url="" silently produced a broken empty host
    # instead of falling back to the OpenAI SDK's real default endpoint.
    assert providers.providers_mapping["openai"].base_url is None


def test_custom_provider_without_base_url_exits_cleanly(use_remote, monkeypatch, capsys):
    monkeypatch.setenv("AI_COMMIT_PROVIDER", "custom")
    monkeypatch.delenv("AI_COMMIT_PROVIDER_BASE_URL", raising=False)
    # Rebuild the "custom" provider entry since it's normally computed once
    # at import time from env vars.
    providers.providers_mapping["custom"] = providers.Provider(
        name="custom", model="some-model", base_url=None
    )
    with pytest.raises(SystemExit):
        providers.get_ai_provider()
    assert "No base URL set" in capsys.readouterr().out


def test_known_remote_provider_without_model_exits_cleanly(
    use_remote, monkeypatch, capsys
):
    monkeypatch.setenv("AI_COMMIT_PROVIDER", "groq")
    monkeypatch.delenv("AI_COMMIT_MODEL", raising=False)
    providers.providers_mapping["groq"].model = None
    with pytest.raises(SystemExit):
        providers.get_ai_provider()
    assert "No model name set" in capsys.readouterr().out
