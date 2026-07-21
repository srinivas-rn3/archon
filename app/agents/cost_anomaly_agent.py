import json
from langchain_aws import ChatBedrockConverse
from app.prompts.cost_anomaly_prompt import COST_ANOMALY_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_COST_ANOMALY, AWS_REGION
from app.tools.cost_explorer_api import get_daily_cost_by_service, detect_anomalies


cost_anomaly_llm = ChatBedrockConverse(
    model=MODEL_COST_ANOMALY,
    region_name=AWS_REGION,
)


def cost_anomaly_agent_node(state: AgentState) -> AgentState:
    """
    Fetches real AWS cost data, detects anomalies using plain code
    (not AI — cost math must be exact), then asks the LLM to explain
    the findings in plain language.
    """
    cost_data = get_daily_cost_by_service(days=7)
    anomalies = detect_anomalies(cost_data, threshold_percent=30.0)

    context = f"Anomalies detected:\n{json.dumps(anomalies, indent=2)}"

    response = cost_anomaly_llm.invoke(
        [
            {"role": "system", "content": COST_ANOMALY_PROMPT},
            {"role": "user", "content": context},
        ]
    )

    state["messages"].append({"role": "assistant", "content": response.content})
    return state