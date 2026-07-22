from langchain_aws import ChatBedrockConverse
from app.prompts.summary_prompt import SUMMARY_AGENT_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_SUMMARY, AWS_REGION
from app.tools.retry_utils import with_retry


summary_llm = ChatBedrockConverse(
    model=MODEL_SUMMARY,
    region_name=AWS_REGION,
)


@with_retry
def _call_llm(last_message: str):
    """Isolated so the retry decorator wraps only the network call."""
    return summary_llm.invoke(
        [
            {"role": "system", "content": SUMMARY_AGENT_PROMPT},
            {"role": "user", "content": last_message},
        ]
    )


def summary_agent_node(state: AgentState) -> AgentState:
    """
    Takes the user's latest message (the text they want summarized)
    and returns a concise summary. Retries automatically on transient
    Bedrock failures.
    """
    last_message = state["messages"][-1].content

    state["text_to_summarize"] = last_message

    try:
        response = _call_llm(last_message)
        content = response.content
        state["summary_result"] = content
    except Exception as e:
        content = f"Sorry, I couldn't generate the summary right now (repeated failures): {e}"
        state["summary_result"] = None

    state["messages"].append({"role": "assistant", "content": content})
    return state