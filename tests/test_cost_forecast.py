import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.graph.build_graph import app_graph

state = {
    "messages": [{"role": "user", "content": "what will my AWS costs look like next month?"}],
    "next_agent": None,
    "text_to_summarize": None,
    "summary_result": None,
}

result = app_graph.invoke(state)

print("SUPERVISOR DECIDED:", repr(result["next_agent"]))
print("FINAL RESPONSE:", result["messages"][-1].content)