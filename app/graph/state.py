from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared state that flows through the entire graph.
    Every agent reads from and writes to this same object.
    """

    # The full conversation history (user + agent messages).
    # `add_messages` tells LangGraph to APPEND new messages,
    # not overwrite the whole list each time.
    messages: Annotated[list, add_messages]

    # Which agent the supervisor decided should handle this turn.
    # e.g. "summary", "code_sql", "scheduler", "github"
    next_agent: Optional[str]

    # The raw text the user wants summarized (if using the Summary agent).
    text_to_summarize: Optional[str]

    # The final summary produced by the Summary agent.
    summary_result: Optional[str]