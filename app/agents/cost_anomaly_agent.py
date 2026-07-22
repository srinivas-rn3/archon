import json
from langchain_aws import ChatBedrockConverse
from app.prompts.cost_anomaly_prompt import COST_ANOMALY_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_COST_ANOMALY, AWS_REGION
from app.tools.cost_explorer_api import get_daily_cost_by_service, detect_anomalies
from app.tools.retry_utils import with_retry


cost_anomaly_llm = ChatBedrockConverse(
    model=MODEL_COST_ANOMALY,
    region_name=AWS_REGION,
)


@with_retry
def _call_llm(context: str):
    """Isolated so the retry decorator wraps only the network call."""
    return cost_anomaly_llm.invoke(
        [
            {"role": "system", "content": COST_ANOMALY_PROMPT},
            {"role": "user", "content": context},
        ]
    )


def cost_anomaly_agent_node(state: AgentState) -> AgentState:
    """
    Fetches real AWS cost data, detects anomalies using plain code
    (not AI — cost math must be exact), then asks the LLM to explain
    the findings in plain language. Retries automatically on transient
    Bedrock failures.
    """
    cost_data = get_daily_cost_by_service(days=7)
    anomalies = detect_anomalies(cost_data, threshold_percent=30.0)

    context = f"Anomalies detected:\n{json.dumps(anomalies, indent=2)}"

    try:
        response = _call_llm(context)
        content = response.content
    except Exception as e:
        content = f"Sorry, I couldn't analyze cost anomalies right now (repeated failures): {e}"

    state["messages"].append({"role": "assistant", "content": content})
    return state