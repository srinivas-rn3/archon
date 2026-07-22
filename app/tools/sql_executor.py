from sqlalchemy import text, inspect
from app.db.session import SessionLocal, engine


def get_schema_description() -> str:
    """
    Reads the actual tables and columns from the database and returns
    a plain-text description the LLM can use to write accurate SQL,
    instead of guessing table/column names.
    """
    inspector = inspect(engine)
    lines = []

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        column_list = ", ".join(f"{col['name']} ({col['type']})" for col in columns)
        lines.append(f"Table: {table_name}\nColumns: {column_list}")

    return "\n\n".join(lines)


def run_safe_query(sql_query: str):
    """
    Executes a SQL query against the database — but ONLY if it's a
    read-only SELECT statement. This is a safety guard: since the agent
    generates SQL from natural language, we never want it accidentally
    running DELETE, DROP, UPDATE, etc. against a real database.
    """

    cleaned = sql_query.strip().lower()

    if not cleaned.startswith("select"):
        return {
            "error": "Only SELECT queries can be executed automatically. "
                     "This query was not run for safety reasons."
        }

    # Extra guard: block common destructive keywords even inside a SELECT
    # (e.g. a subquery trying something sneaky)
    blocked_keywords = ["drop", "delete", "update", "insert", "alter", "truncate"]
    if any(keyword in cleaned for keyword in blocked_keywords):
        return {"error": "Query contains a blocked keyword and was not run."}

    db = SessionLocal()
    try:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        columns = result.keys()
        return {"columns": list(columns), "rows": [list(row) for row in rows]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()