from langchain_aws import ChatBedrockConverse
from app.prompts.summary_prompt import SUMMARY_AGENT_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_SUMMARY, AWS_REGION


summary_llm = ChatBedrockConverse(
    model=MODEL_SUMMARY,
    region_name=AWS_REGION,
)


def summary_agent_node(state: AgentState) -> AgentState:
    """
    Takes the user's latest message (the text they want summarized)
    and returns a concise summary.
    """
    last_message = state["messages"][-1].content

    # Store the raw text in state too, in case other agents/tools
    # want to reference what was summarized later.
    state["text_to_summarize"] = last_message

    response = summary_llm.invoke(
        [
            {"role": "system", "content": SUMMARY_AGENT_PROMPT},
            {"role": "user", "content": last_message},
        ]
    )

    state["summary_result"] = response.content
    state["messages"].append({"role": "assistant", "content": response.content})

    return state