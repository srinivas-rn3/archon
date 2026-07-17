from app.graph import supervisor


class DummyLLM:
    def invoke(self, messages):
        raise RuntimeError("bedrock unavailable")


def test_supervisor_routes_github_queries_to_github(monkeypatch):
    monkeypatch.setattr(supervisor, "supervisor_llm", DummyLLM())

    state = {
        "messages": [{"role": "user", "content": "show me recent activity on srinivas-rn3/archon"}],
        "next_agent": None,
        "text_to_summarize": None,
        "summary_result": None,
    }

    result = supervisor.supervisor_node(state)

    assert result["next_agent"] == "github"
