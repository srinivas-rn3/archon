import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.graph.build_graph import app_graph

state = {
    "messages": [{
        "role": "user",
        "content": "Summarize this: LangGraph is a framework for building stateful, multi-agent applications with LLMs. It represents workflows as graphs, where nodes are functions or agents and edges define how control flows between them. It supports checkpointing, letting you save and resume execution state, which is useful for debugging and human-in-the-loop workflows."
    }],
    "next_agent": None,
    "text_to_summarize": None,
    "summary_result": None,
}

result = app_graph.invoke(state)

print("SUPERVISOR DECIDED:", repr(result["next_agent"]))
print("FINAL RESPONSE:", result["messages"][-1].content)