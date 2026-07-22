import json
from langchain_aws import ChatBedrockConverse
from app.prompts.cost_forecast_prompt import COST_FORECAST_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_COST_FORECAST, AWS_REGION
from app.tools.cost_explorer_api import get_cost_forecast
from app.tools.retry_utils import with_retry


cost_forecast_llm = ChatBedrockConverse(
    model=MODEL_COST_FORECAST,
    region_name=AWS_REGION,
)


@with_retry
def _call_llm(context: str):
    """Isolated so the retry decorator wraps only the network call, not the whole node."""
    return cost_forecast_llm.invoke(
        [
            {"role": "system", "content": COST_FORECAST_PROMPT},
            {"role": "user", "content": context},
        ]
    )


def cost_forecast_agent_node(state: AgentState) -> AgentState:
    """
    Fetches AWS's own cost forecast (real prediction, not AI-generated),
    then asks the LLM to explain it in plain language.
    Retries automatically on transient Bedrock failures.
    """
    forecast = get_cost_forecast(days_ahead=30)

    context = f"Forecast data:\n{json.dumps(forecast, indent=2)}"

    try:
        response = _call_llm(context)
        content = response.content
    except Exception as e:
        content = f"Sorry, I couldn't generate the forecast explanation right now (repeated failures): {e}"

    state["messages"].append({"role": "assistant", "content": content})
    return state