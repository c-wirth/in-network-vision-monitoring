# db_infrastructure/db_components/connections.py

"""
This file is responsible for setting up and managing the database connection.

It handles:
- Reading the database URL from environment variables
- Creating the database engine (the connection to the DB)
- Creating a session factory (used to interact with the DB)
- Providing a safe session per request (for FastAPI)
- Initializing database tables (for development)

IMPORTANT:
- This file does NOT contain queries or business logic
- Other parts of the app should ONLY interact with the DB through sessions provided here
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 1. CONFIGURATION
# ============================================================

# Read the database URL from environment variables
# Example: "sqlite:///app.db"
DATABASE_URL = os.getenv("DATABASE_URL")


print("DATABASE_URL:", DATABASE_URL)
print("DB FILE EXISTS:", os.path.exists(DATABASE_URL.replace("sqlite:///", "")))

# Fail fast if DATABASE_URL is not set
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")


# ============================================================
# 2. ENGINE SETUP
# ============================================================

# The engine is the core connection to the database
# For SQLite, we must disable same-thread checking for FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)


# ============================================================
# 3. SESSION FACTORY
# ============================================================

# A session is how we talk to the database (run queries, insert data, etc.)
# sessionmaker creates new session objects when called
SessionLocal = sessionmaker(
    autocommit=False,   # we will manually control commits
    autoflush=False,    # prevents automatic DB writes before commit
    bind=engine         # bind sessions to our engine
)


# ============================================================
# 4. SESSION SCOPE (DEPENDENCY)
# ============================================================

def get_db():
    """
    Provides a database session for a single request.

    Usage (in FastAPI):
        db: Session = Depends(get_db)

    What this function does:
    - Creates a new session
    - Yields it to the caller
    - Rolls back if an error occurs
    - Closes the session when done

    This ensures:
    - No session leaks
    - Safe concurrent usage
    """

    db = SessionLocal()
    try:
        yield db
    except Exception:
        # If something goes wrong, undo any changes
        db.rollback()
        raise
    finally:
        # Always close the session to free resources
        db.close()


# ============================================================
# 5. DATABASE INITIALIZATION (DEV ONLY)
# ============================================================

def init_db():
    """
    Creates all tables in the database.

    Ensures models are imported so SQLAlchemy knows about them.
    """

    # Import models so they are registered with Base.metadata
    # Without this, tables may not be created

    from core.db_infrastructure.db_components.models import User, Clip

    Base.metadata.create_all(bind=engine)