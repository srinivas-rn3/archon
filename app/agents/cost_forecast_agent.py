import json
from langchain_aws import ChatBedrockConverse
from app.prompts.cost_forecast_prompt import COST_FORECAST_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_COST_FORECAST, AWS_REGION
from app.tools.cost_explorer_api import get_cost_forecast


cost_forecast_llm = ChatBedrockConverse(
    model=MODEL_COST_FORECAST,
    region_name=AWS_REGION,
)


def cost_forecast_agent_node(state: AgentState) -> AgentState:
    """
    Fetches AWS's own cost forecast (real prediction, not AI-generated),
    then asks the LLM to explain it in plain language.
    """
    forecast = get_cost_forecast(days_ahead=30)

    context = f"Forecast data:\n{json.dumps(forecast, indent=2)}"

    response = cost_forecast_llm.invoke(
        [
            {"role": "system", "content": COST_FORECAST_PROMPT},
            {"role": "user", "content": context},
        ]
    )

    state["messages"].append({"role": "assistant", "content": response.content})
    return state