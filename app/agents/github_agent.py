from langchain_aws import ChatBedrockConverse
from app.prompts.github_prompt import GITHUB_AGENT_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_GITHUB, AWS_REGION, GITHUB_DEFAULT_USERNAME, GITHUB_DEFAULT_REPO
from app.tools.github_api import get_recent_commits, get_open_pull_requests


github_llm = ChatBedrockConverse(
    model=MODEL_GITHUB,
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
    last_message = state["messages"][-1].content

    username, repo = extract_repo_info(last_message)

    # Step 1: get the raw data using our tool functions (no AI involved here)
    commits = get_recent_commits(username, repo, limit=5)
    prs = get_open_pull_requests(username, repo)

    raw_data = f"Recent commits:\n{commits}\n\nOpen pull requests:\n{prs}"

    # Step 2: ask the LLM to turn that raw data into a readable summary
    response = github_llm.invoke(
        [
            {"role": "system", "content": GITHUB_AGENT_PROMPT},
            {"role": "user", "content": raw_data},
        ]
    )

    state["messages"].append({"role": "assistant", "content": response.content})
    return state