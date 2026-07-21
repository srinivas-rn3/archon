from langchain_aws import ChatBedrockConverse
from app.prompts.supervisor_prompt import SUPERVISOR_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_SUPERVISOR, AWS_REGION


# Supervisor uses the cheapest/fastest model — routing is a simple decision,
# not a task that needs deep reasoning. Model is set in config.py, not here.
supervisor_llm = ChatBedrockConverse(
    model=MODEL_SUPERVISOR,
    region_name=AWS_REGION,
)

VALID_AGENTS = {"cost_anomaly", "cost_forecast", "summary", "github"}


def supervisor_node(state: AgentState) -> AgentState:
    """
    Reads the latest user message and decides which agent should handle it.
    Writes the decision into state['next_agent'].
    """

    # Get the most recent user message from the conversation history
    last_message = state["messages"][-1].content

    # Ask the LLM to classify which agent should handle this
    response = supervisor_llm.invoke(
        [
            {"role": "system", "content": SUPERVISOR_PROMPT},
            {"role": "user", "content": last_message},
        ]
    )

    raw_response = response.content.strip().lower()

    # Robust parsing: check if any valid agent name appears in the response,
    # rather than requiring an exact match (models sometimes add extra words
    # even when told not to).
    decision = "unclear"
    for agent_name in VALID_AGENTS:
        if agent_name in raw_response:
            decision = agent_name
            break

    state["next_agent"] = decision
    return state


def route_decision(state: AgentState) -> str:
    """
    Tells LangGraph which node to go to next, based on the supervisor's decision.
    Used as the routing function in build_graph.py.
    """
    return state["next_agent"]