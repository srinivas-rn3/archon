import json
from datetime import date, datetime, time
from langchain_aws import ChatBedrockConverse
from app.prompts.scheduler_prompt import SCHEDULER_AGENT_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_SCHEDULER, AWS_REGION
from app.tools.scheduler_db import create_task


scheduler_llm = ChatBedrockConverse(
    model=MODEL_SCHEDULER,
    region_name=AWS_REGION,
)

# Optional: use dateparser for deterministic relative date parsing when available.
try:
    import dateparser
    _HAS_DATEPARSER = True
except Exception:
    _HAS_DATEPARSER = False


def _simple_relative_date_parser(text: str):
    """Lightweight parsing for common relative phrases without external deps.
    Returns an ISO date string or None.
    """
    import re
    from datetime import timedelta

    txt = text.lower()
    today_dt = date.today()

    if "today" in txt:
        return today_dt.isoformat()
    if "tomorrow" in txt:
        return (today_dt + timedelta(days=1)).isoformat()
    if "day after tomorrow" in txt:
        return (today_dt + timedelta(days=2)).isoformat()

    m = re.search(r"in\s+(\d+)\s+day", txt)
    if m:
        days = int(m.group(1))
        return (today_dt + timedelta(days=days)).isoformat()

    # Weekday names
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    for name, idx in weekdays.items():
        if re.search(rf"\b(next|this)?\s*{name}\b", txt):
            today_idx = today_dt.weekday()
            days_ahead = (idx - today_idx) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (today_dt + timedelta(days=days_ahead)).isoformat()

    return None


def scheduler_agent_node(state: AgentState) -> AgentState:
    """
    Extracts a task description + due date from the user's message,
    then saves it to the database.
    """
    last_message = state["messages"][-1].content

    # Try to deterministically parse any relative date phrases from the user's message
    parsed_due_date = None
    if _HAS_DATEPARSER:
        try:
            base = datetime.combine(date.today(), time.min)
            parsed = dateparser.parse(last_message, settings={"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"})
            if parsed:
                parsed_due_date = parsed.date().isoformat()
        except Exception:
            parsed_due_date = None
    else:
        # Fallback to a lightweight parser for common phrases
        parsed_due_date = _simple_relative_date_parser(last_message)

    prompt = SCHEDULER_AGENT_PROMPT.format(today_date=date.today().isoformat())

    response = scheduler_llm.invoke(
        [
            {"role": "system", "content": prompt},
            {"role": "user", "content": last_message},
        ]
    )

    # Parse the model's JSON response
    try:
        task_data = json.loads(response.content.strip())
    except json.JSONDecodeError:
        state["messages"].append({
            "role": "assistant",
            "content": "I couldn't understand that as a task. Could you rephrase it?"
        })
        return state

    # If we deterministically parsed a date from the user's utterance, prefer that
    # over the model's returned date (this avoids ambiguous LLM date interpretations).
    if parsed_due_date:
        task_data["due_date"] = parsed_due_date

    # Actually save it to the database
    result = create_task(
        description=task_data.get("description", "Untitled task"),
        due_date=task_data.get("due_date"),
    )

    if "error" in result:
        reply = f"Something went wrong saving that task: {result['error']}"
    else:
        due = f" (due {result['due_date']})" if result["due_date"] else ""
        reply = f"Task saved: \"{result['description']}\"{due}"

    state["messages"].append({"role": "assistant", "content": reply})
    return state