from fastapi import APIRouter
from pydantic import BaseModel
from app.graph.build_graph import app_graph

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    agent_used: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Takes a user message, runs it through the full agent graph
    (Supervisor -> Agent -> Guardrail), and returns the response.
    """
    state = {
        "messages": [{"role": "user", "content": request.message}],
        "next_agent": None,
        "text_to_summarize": None,
        "summary_result": None,
    }

    result = app_graph.invoke(state)

    reply = result["messages"][-1].content if hasattr(result["messages"][-1], "content") else result["messages"][-1]["content"]

    return ChatResponse(reply=reply, agent_used=result["next_agent"])