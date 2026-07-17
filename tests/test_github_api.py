from app.tools import github_api


def test_build_headers_omits_authorization_without_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    headers = github_api.build_headers()

    assert headers["Accept"] == "application/vnd.github+json"
    assert "Authorization" not in headers


def test_build_headers_uses_current_environment_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "abc123")

    headers = github_api.build_headers()

    assert headers["Authorization"] == "token abc123"
