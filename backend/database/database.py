# """
# Database configuration and session management.
# """
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from typing import Generator
# from config import settings

# # Create database engine
# engine = create_engine(
#     settings.DATABASE_URL,
#     pool_pre_ping=True,  # Verify connections before using
#     pool_size=10,  # Connection pool size
#     max_overflow=20  # Allow up to 20 additional connections
# )

# # Create session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base class for ORM models
# Base = declarative_base()


# def get_db() -> Generator[Session, None, None]:
#     """
#     Dependency for getting database session.
    
#     Yields:
#         Database session
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def init_db():
#     """Initialize database - create all tables."""
#     Base.metadata.create_all(bind=engine)



"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from config import settings

# Check if we are using SQLite
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Create database engine
if is_sqlite:
    # SQLite fix: remove pooling and add thread safety
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Original settings for PostgreSQL/MySQL
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)