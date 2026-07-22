import streamlit as st
from datetime import datetime
from app.graph.build_graph import app_graph
from app.graph.supervisor import supervisor_node, route_decision
from app.agents.github_agent import github_agent_node
from app.agents.summary_agent import summary_agent_node
from app.agents.cost_anomaly_agent import cost_anomaly_agent_node
from app.agents.cost_forecast_agent import cost_forecast_agent_node
from app.graph.guardrail_node import guardrail_node

st.set_page_config(page_title="Archon", page_icon="🧭", layout="wide")

AGENT_NODES = {
    "github": github_agent_node,
    "summary": summary_agent_node,
    "cost_anomaly": cost_anomaly_agent_node,
    "cost_forecast": cost_forecast_agent_node,
}

AGENT_COLORS = {
    "github": "#8B7FD6",
    "summary": "#6FA8A0",
    "cost_anomaly": "#D68B4A",
    "cost_forecast": "#5FA8D6",
    "unclear": "#7A7F87",
}

# --- Session state setup ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logs" not in st.session_state:
    st.session_state.logs = []


def run_agent(user_message: str, forced_agent: str | None):
    """
    Runs the message either through the full Supervisor-routed graph,
    or directly through one chosen agent (bypassing routing), then
    always through the guardrail check.
    """
    state = {
        "messages": [{"role": "user", "content": user_message}],
        "next_agent": forced_agent,
        "text_to_summarize": None,
        "summary_result": None,
    }

    if forced_agent is None:
        # Auto mode: run the full graph (Supervisor decides)
        result = app_graph.invoke(state)
        agent_used = result["next_agent"]
    else:
        # Manual mode: skip the Supervisor, call the chosen agent directly
        state = AGENT_NODES[forced_agent](state)
        state = guardrail_node(state)
        result = state
        agent_used = forced_agent

    reply = result["messages"][-1]
    reply_text = reply.content if hasattr(reply, "content") else reply["content"]

    return reply_text, agent_used


# --- Sidebar: agent selection + logs ---
with st.sidebar:
    st.markdown("### Archon")
    st.caption("Multi-agent AWS & dev assistant")

    mode = st.radio(
        "Routing mode",
        ["Auto (Supervisor decides)", "Manual (pick an agent)"],
    )

    forced_agent = None
    if mode == "Manual (pick an agent)":
        forced_agent = st.selectbox("Run directly:", list(AGENT_NODES.keys()))

    st.divider()
    st.markdown("### Session logs")

    if not st.session_state.logs:
        st.caption("No calls yet this session.")
    else:
        for log in reversed(st.session_state.logs):
            color = AGENT_COLORS.get(log["agent"], "#7A7F87")
            st.markdown(
                f"""<div style="border-left:3px solid {color}; padding-left:8px; margin-bottom:10px;">
                <span style="font-size:11px; color:{color}; font-weight:600; text-transform:uppercase;">{log['agent']}</span><br>
                <span style="font-size:11px; color:#888;">{log['time']}</span><br>
                <span style="font-size:12px;">{log['message'][:60]}{'...' if len(log['message']) > 60 else ''}</span>
                </div>""",
                unsafe_allow_html=True,
            )

# --- Main chat area ---
st.markdown("## Ask Archon")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("agent"):
            color = AGENT_COLORS.get(msg["agent"], "#7A7F87")
            st.markdown(
                f"<span style='font-size:11px; color:{color}; font-weight:600; text-transform:uppercase;'>{msg['agent']}</span>",
                unsafe_allow_html=True,
            )
        st.write(msg["content"])

user_input = st.chat_input("Ask about AWS costs, GitHub activity, or summarize something…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Routing…" if forced_agent is None else f"Running {forced_agent}…"):
            reply_text, agent_used = run_agent(user_input, forced_agent)

        color = AGENT_COLORS.get(agent_used, "#7A7F87")
        st.markdown(
            f"<span style='font-size:11px; color:{color}; font-weight:600; text-transform:uppercase;'>{agent_used}</span>",
            unsafe_allow_html=True,
        )
        st.write(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text, "agent": agent_used})
    st.session_state.logs.append({
        "agent": agent_used,
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": user_input,
    })