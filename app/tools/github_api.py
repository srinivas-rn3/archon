import os

import requests

GITHUB_API_BASE = "https://api.github.com"


def build_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def _get_json(url: str, params: dict | None = None):
    response = requests.get(url, headers=build_headers(), params=params, timeout=10)
    if response.status_code == 401:
        return None
    response.raise_for_status()
    return response.json()


def get_recent_commits(username: str, repo: str, limit: int = 5):
    """
    Fetches the most recent commits for a given repo.
    Example: get_recent_commits("srinivas-rn3", "archon")
    """
    url = f"{GITHUB_API_BASE}/repos/{username}/{repo}/commits"
    commits = _get_json(url, params={"per_page": limit}) or []
    return [
        {
            "message": c["commit"]["message"],
            "author": c["commit"]["author"]["name"],
            "date": c["commit"]["author"]["date"],
            "sha": c["sha"][:7],
        }
        for c in commits
    ]


def get_open_pull_requests(username: str, repo: str):
    """
    Fetches currently open pull requests for a given repo.
    """
    url = f"{GITHUB_API_BASE}/repos/{username}/{repo}/pulls"
    prs = _get_json(url, params={"state": "open"}) or []
    return [
        {
            "title": pr["title"],
            "author": pr["user"]["login"],
            "created_at": pr["created_at"],
            "url": pr["html_url"],
        }
        for pr in prs
    ]


def get_user_activity_summary(username: str):
    """
    Fetches a user's recent public GitHub events
    (pushes, PR activity, issue activity, etc.)
    """
    url = f"{GITHUB_API_BASE}/users/{username}/events/public"
    events = _get_json(url, params={"per_page": 10}) or []
    return [
        {
            "type": e["type"],
            "repo": e["repo"]["name"],
            "created_at": e["created_at"],
        }
        for e in events
    ]