from datetime import datetime, date
try:
    import dateparser
    _HAS_DATEPARSER = True
except Exception:
    _HAS_DATEPARSER = False
from app.db.session import SessionLocal
from app.db.models import Task


def create_task(description: str, due_date: str | None = None, user_id: str | None = None):
    """
    Saves a new task to the database.
    due_date should be a string like 'YYYY-MM-DD' or None.
    """
    db = SessionLocal()
    try:
        parsed_date = None
        if due_date:
            # Accept either ISO date strings or let dateparser handle natural text
            if _HAS_DATEPARSER:
                parsed = dateparser.parse(due_date)
                if parsed:
                    parsed_date = parsed.date()
            else:
                # Expect YYYY-MM-DD
                parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()

        task = Task(
            description=description,
            due_date=parsed_date,
            user_id=user_id,
            status="pending",
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Normalize returned due_date to ISO date string (date-only)
        td = task.due_date
        if td is not None:
            try:
                # if it's a datetime, convert to date
                from datetime import datetime as _dt
                if isinstance(td, _dt):
                    due_iso = td.date().isoformat()
                else:
                    due_iso = td.isoformat()
            except Exception:
                due_iso = str(td)
        else:
            due_iso = None
        return {"id": task.id, "description": task.description, "due_date": due_iso, "status": task.status}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def list_pending_tasks(user_id: str | None = None):
    """Fetches all pending tasks, optionally filtered by user."""
    db = SessionLocal()
    try:
        query = db.query(Task).filter(Task.status == "pending")
        if user_id:
            query = query.filter(Task.user_id == user_id)

        tasks = query.order_by(Task.due_date).all()
        out = []
        for t in tasks:
            td = t.due_date
            if td is not None:
                try:
                    from datetime import datetime as _dt
                    if isinstance(td, _dt):
                        due_iso = td.date().isoformat()
                    else:
                        due_iso = td.isoformat()
                except Exception:
                    due_iso = str(td)
            else:
                due_iso = None
            out.append({"id": t.id, "description": t.description, "due_date": due_iso, "status": t.status})
        return out
    finally:
        db.close()