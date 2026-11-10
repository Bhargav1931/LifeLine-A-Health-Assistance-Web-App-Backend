import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file if present
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration for PostgreSQL
raw_database_url = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5434/lifeline_db"
)

# Render & Cloud DB Compatibility:
# Ensure SQLAlchemy explicitly uses psycopg2 driver (postgresql+psycopg2://)
# This fixes the Python 3.14 / SQLAlchemy 2.0+ error: "No module named 'psycopg'"
if raw_database_url.startswith("postgres://"):
    DATABASE_URL = raw_database_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif raw_database_url.startswith("postgresql://"):
    DATABASE_URL = raw_database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    DATABASE_URL = raw_database_url

logger.info(f"Connecting to database at {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
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
