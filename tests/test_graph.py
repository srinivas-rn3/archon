import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.graph.build_graph import app_graph
"""
state = {
    "messages": [{"role": "user", "content": "show me recent activity on srinivas-rn3/archon"}],
    "next_agent": None,
    "text_to_summarize": None,
    "summary_result": None,
}

result = app_graph.invoke(state)
last_message = result["messages"][-1]
content = getattr(last_message, "content", None)
if content is None and isinstance(last_message, dict):
    content = last_message.get("content")
print(content)
"""
state = {
    "messages": [{"role": "user", "content": "show me recent activity on srinivas-rn3/archon"}],
    "next_agent": None,
    "text_to_summarize": None,
    "summary_result": None,
}
 
result = app_graph.invoke(state)
 
#print("SUPERVISOR DECIDED:", repr(result["next_agent"]))
#print("FINAL RESPONSE:", result["messages"][-1]["content"])
print(result["messages"][-1].content)