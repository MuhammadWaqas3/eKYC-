"""
Database initialization script.
Run this to create all database tables.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db, engine
from database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database."""
    try:
        logger.info("Creating database tables...")
        init_db()
        logger.info("✓ Database tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"✓ Created {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table}")
            
    except Exception as e:
        logger.error(f"✗ Error creating database: {e}")
        raise

if __name__ == "__main__":
    main()
