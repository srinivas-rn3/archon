import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agents import github_agent


class DummyLLM:
    def invoke(self, messages):
        raise NotImplementedError("Provider qwen model does not support chat")


def test_github_agent_node_falls_back_when_llm_is_unavailable(monkeypatch):
    monkeypatch.setattr(github_agent, "github_llm", DummyLLM())
    monkeypatch.setattr(
        github_agent,
        "get_recent_commits",
        lambda username, repo, limit=5: [
            {"message": "Add tests", "author": "Ada", "date": "2026-01-01", "sha": "abc1234"}
        ],
    )
    monkeypatch.setattr(github_agent, "get_open_pull_requests", lambda username, repo: [])

    state = {
        "messages": [{"role": "user", "content": "show me recent activity on srinivas-rn3/archon"}],
        "next_agent": None,
        "text_to_summarize": None,
        "summary_result": None,
    }

    result = github_agent.github_agent_node(state)

    assert result["messages"][-1]["content"].startswith("Recent activity summary")
    assert "Add tests" in result["messages"][-1]["content"]
