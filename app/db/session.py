from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# The engine is the actual connection to Postgres.
engine = create_engine(DATABASE_URL)

# SessionLocal is used to talk to the DB (read/write) in each request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is what our table definitions (models.py) will inherit from.
Base = declarative_base()


def get_db():
    """
    Gives you a database session to use, and makes sure it's
    closed properly afterward — even if something goes wrong.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()