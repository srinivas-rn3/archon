from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func
from app.db.session import Base


class Conversation(Base):
    """One row per chat thread."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    thread_id = Column(String, unique=True, nullable=False)  # links to LangGraph checkpoints
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    """Used by the Scheduler agent — one row per task/reminder."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String, default="pending")  # pending / done / cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgentLog(Base):
    """One row per agent call — for your own cost/usage tracking (separate from LangSmith)."""
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True)
    agent_name = Column(String, nullable=False)      # e.g. "summary", "code_sql"
    model_used = Column(String, nullable=False)       # e.g. "qwen.qwen3-32b-v1:0"
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    status = Column(String, default="success")         # success / error
    created_at = Column(DateTime(timezone=True), server_default=func.now())