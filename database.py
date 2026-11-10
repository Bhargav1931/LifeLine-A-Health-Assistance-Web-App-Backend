import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration for PostgreSQL
# Default connects to local PostgreSQL container on port 5434 or configured DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5434/lifeline_db"
)

logger.info(f"Connecting to database at {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    FastAPI dependency that yields a SQLAlchemy database session
    and ensures it is properly closed when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
