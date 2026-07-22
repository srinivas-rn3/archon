from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.supervisor import supervisor_node, route_decision
from app.graph.guardrail_node import guardrail_node
from app.agents.github_agent import github_agent_node
from app.agents.summary_agent import summary_agent_node
from app.agents.cost_anomaly_agent import cost_anomaly_agent_node
from app.agents.cost_forecast_agent import cost_forecast_agent_node


def placeholder_node(state: AgentState) -> AgentState:
    """
    Temporary stand-in for agents we haven't built yet.
    """
    state["messages"].append(
        {
            "role": "assistant",
            "content": "This agent isn't built yet — coming soon.",
        }
    )
    return state


def build_graph():
    """
    Wires the Supervisor, all agents, and the guardrail check into one
    runnable graph. Every agent's output now passes through the
    guardrail node before reaching the user.
    """
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("github", github_agent_node)
    graph.add_node("summary", summary_agent_node)
    graph.add_node("cost_anomaly", cost_anomaly_agent_node)
    graph.add_node("cost_forecast", cost_forecast_agent_node)
    graph.add_node("unclear", placeholder_node)
    graph.add_node("guardrail", guardrail_node)  # new: exit gate for all agents

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "github": "github",
            "summary": "summary",
            "cost_anomaly": "cost_anomaly",
            "cost_forecast": "cost_forecast",
            "unclear": "unclear",
        },
    )

    # Every agent now routes through the guardrail before ending,
    # instead of going straight to END.
    graph.add_edge("github", "guardrail")
    graph.add_edge("summary", "guardrail")
    graph.add_edge("cost_anomaly", "guardrail")
    graph.add_edge("cost_forecast", "guardrail")
    graph.add_edge("unclear", "guardrail")

    graph.add_edge("guardrail", END)

    return graph.compile()


app_graph = build_graph()