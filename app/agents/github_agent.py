from langchain_aws import ChatBedrock
from app.prompts.github_prompt import GITHUB_AGENT_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_GITHUB, AWS_REGION, GITHUB_DEFAULT_USERNAME, GITHUB_DEFAULT_REPO
from app.tools.github_api import get_recent_commits, get_open_pull_requests


github_llm = ChatBedrock(
    model_id=MODEL_GITHUB,
    region_name=AWS_REGION,
)


def extract_repo_info(user_message: str) -> tuple[str, str]:
    """
    Very simple v1 logic: if the user mentions "username/repo" format,
    use that. Otherwise, fall back to the default repo from config.

    Example: "show commits on srinivas-rn3/archon" -> ("srinivas-rn3", "archon")
    """
    import re

    match = re.search(r"([\w-]+)/([\w-]+)", user_message)
    if match:
        return match.group(1), match.group(2)

    return GITHUB_DEFAULT_USERNAME, GITHUB_DEFAULT_REPO


def github_agent_node(state: AgentState) -> AgentState:
    """
    Fetches GitHub data (commits + open PRs) and asks the LLM to
    summarize it in plain language for the user.
    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "content"):
        last_text = last_message.content
    elif isinstance(last_message, dict) and "content" in last_message:
        last_text = last_message["content"]
    else:
        raise ValueError("The last message must expose .content or contain a 'content' field")

    username, repo = extract_repo_info(last_text)

    commits = get_recent_commits(username, repo, limit=5)
    prs = get_open_pull_requests(username, repo)

    raw_data = f"Recent commits:\n{commits}\n\nOpen pull requests:\n{prs}"

    try:
        response = github_llm.invoke(
            [
                {"role": "system", "content": GITHUB_AGENT_PROMPT},
                {"role": "user", "content": raw_data},
            ]
        )
        summary = response.content if hasattr(response, "content") else str(response)
    except (Exception, NotImplementedError):
        commit_lines = "\n".join(
            f"- {commit['message']} by {commit['author']} on {commit['date']}"
            for commit in commits
        )
        pr_lines = "\n".join(
            f"- {pr['title']} by {pr['author']}"
            for pr in prs
        )
        summary = (
            "Recent activity summary:\n"
            f"Recent commits:\n{commit_lines or '- None'}\n\n"
            f"Open pull requests:\n{pr_lines or '- None'}"
        )

    state["messages"].append({"role": "assistant", "content": summary})
    return state
