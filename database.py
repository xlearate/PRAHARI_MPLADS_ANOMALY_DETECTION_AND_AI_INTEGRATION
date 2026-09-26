"""
PRAHARI Backend - Phase 2 (partial)
------------------------------------
Sets up the SQLite database connection using SQLAlchemy.

NOTE: models.py is intentionally NOT built yet. The ML team found
missing data in the datasets uploaded to the SIH portal and is
still working out what changes that means for the columns. Building
models.py against columns that might change would mean redoing it.

This file only sets up the *connection* - that part doesn't depend
on what the final columns turn out to be, so it's safe to build now.

Once models.py exists, main.py will use `get_db` (below) as a
dependency to get a database session per request.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------------------------------------------------------
# DATABASE URL
# ---------------------------------------------------------------------------
# SQLite stores everything in a single file - prahari.db - which will be
# created automatically the first time the app runs. No separate server,
# no separate install, nothing to configure beyond this line.
#
# If this project later moves to PostgreSQL, only this URL changes -
# nothing else in the app needs to know which database engine is used.
SQLALCHEMY_DATABASE_URL = "sqlite:///./prahari.db"

# ---------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------
# connect_args is SQLite-specific: by default SQLite only allows the thread
# that created a connection to use it, which conflicts with how FastAPI
# handles requests. This setting relaxes that restriction safely for our
# use case (single-file local dev database).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# ---------------------------------------------------------------------------
# SESSION
# ---------------------------------------------------------------------------
# Each API request will get its own database session from this factory.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# BASE
# ---------------------------------------------------------------------------
# All ORM models (to be defined in models.py once the dataset is finalized)
# will inherit from this Base class.
Base = declarative_base()


# ---------------------------------------------------------------------------
# DEPENDENCY
# ---------------------------------------------------------------------------
def get_db():
    """
    FastAPI dependency that provides a database session to a route,
    and guarantees it gets closed afterward even if an error occurs.

    Usage (once models.py + routes exist):

        @app.get("/api/projects")
        def get_projects(db: Session = Depends(get_db)):
            return db.query(Project).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()