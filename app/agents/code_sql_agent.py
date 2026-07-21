from langchain_aws import ChatBedrockConverse
from app.prompts.code_sql_prompt import CODE_SQL_AGENT_PROMPT
from app.graph.state import AgentState
from app.config import MODEL_CODE_SQL, AWS_REGION
from app.tools.sql_executor import get_schema_description


code_sql_llm = ChatBedrockConverse(
    model=MODEL_CODE_SQL,
    region_name=AWS_REGION,
)


def code_sql_agent_node(state: AgentState) -> AgentState:
    """
    Writes code or SQL based on the user's request.
    For SQL requests, the actual database schema is fetched first and
    given to the LLM, so it writes SQL against real tables/columns
    instead of guessing.
    """
    last_message = state["messages"][-1].content

    # Ground the LLM in the real schema, so it doesn't guess table/column names.
    schema = get_schema_description()
    context = f"Here is the actual database schema:\n\n{schema}\n\nUser request: {last_message}"

    response = code_sql_llm.invoke(
        [
            {"role": "system", "content": CODE_SQL_AGENT_PROMPT},
            {"role": "user", "content": context},
        ]
    )

    state["messages"].append({"role": "assistant", "content": response.content})
    return state