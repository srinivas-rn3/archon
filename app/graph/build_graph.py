from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.supervisor import supervisor_node, route_decision
from app.agents.github_agent import github_agent_node
from app.agents.summary_agent import summary_agent_node


def placeholder_node(state: AgentState) -> AgentState:
    """
    Temporary stand-in for agents we haven't built yet
    (code_sql, scheduler, summary). Prevents the graph from
    breaking if the Supervisor routes to one of these.
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
    Wires the Supervisor and all agents into one runnable graph.
    """
    graph = StateGraph(AgentState)

    # Register each node (a node = one agent's function)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("github", github_agent_node)
    graph.add_node("summary", summary_agent_node)
    graph.add_node("code_sql", placeholder_node)
    graph.add_node("scheduler", placeholder_node)
    graph.add_node("unclear", placeholder_node)

    # The graph always starts at the supervisor
    graph.set_entry_point("supervisor")

    # After the supervisor decides, route to the matching agent node.
    # route_decision reads state["next_agent"] and returns the node name.
    graph.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "github": "github",
            "code_sql": "code_sql",
            "scheduler": "scheduler",
            "summary": "summary",
            "unclear": "unclear",
        },
    )

    # After any agent finishes, the graph ends (returns to the user)
    graph.add_edge("github", END)
    graph.add_edge("code_sql", END)
    graph.add_edge("scheduler", END)
    graph.add_edge("summary", END)
    graph.add_edge("unclear", END)

    return graph.compile()


# A ready-to-use compiled graph, importable elsewhere (e.g. FastAPI)
app_graph = build_graph()