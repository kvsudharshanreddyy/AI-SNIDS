"""
database/database.py

Database engine creation and session management for AI-SNIDS.

Uses SQLAlchemy 2.0 style with context manager sessions.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base


# ─── Configuration ─────────────────────────────────────────────────────────────

# Default path: data/ai_snids.db (relative to project root)
# Can be overridden via DATABASE_URL environment variable
_default_db_path = Path(__file__).parent.parent / "data" / "ai_snids.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")

# ─── Engine ────────────────────────────────────────────────────────────────────

# check_same_thread=False is required for SQLite when used across multiple
# threads (e.g., FastAPI async handlers). Safe here because SQLAlchemy
# manages connection pooling internally.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Set to True to log all SQL statements during debugging
)

# ─── Session Factory ───────────────────────────────────────────────────────────

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Public API ────────────────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create all tables if they don't exist yet.

    Safe to call multiple times — SQLAlchemy uses CREATE TABLE IF NOT EXISTS.
    Called once at application startup.
    """
    # Ensure the data directory exists
    db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    print(f"[DB] Database initialized at: {db_path.resolve()}")


def get_session() -> Session:
    """
    Create and return a new database session.

    Usage:
        session = get_session()
        try:
            session.add(event)
            session.commit()
        finally:
            session.close()

    Or use as context manager:
        with get_session() as session:
            ...
    """
    return SessionLocal()


def health_check() -> bool:
    """Verify the database connection is working."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Health check failed: {e}")
        return False
