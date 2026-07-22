from app.graph.state import AgentState
from app.tools.guardrails import redact_pii


def guardrail_node(state: AgentState) -> AgentState:
    """
    Runs after every agent, before the response reaches the user.
    Checks the latest message for PII and redacts it if found.
    This is the single "exit gate" all agent output passes through.
    """
    last_message = state["messages"][-1]

    # Handle both plain dicts and LangChain message objects
    content = last_message.content if hasattr(last_message, "content") else last_message["content"]

    redacted_content, findings = redact_pii(content)

    if findings:
        # Replace the last message with the redacted version.
        # We rebuild the message rather than mutate it in place, since
        # LangChain message objects can be immutable-ish in practice.
        state["messages"][-1] = {"role": "assistant", "content": redacted_content}

        # Log what was caught — for now just print; later this could
        # write to your agent_logs table or LangSmith.
        print(f"[GUARDRAIL] Redacted PII types: {list(findings.keys())}")

    return state