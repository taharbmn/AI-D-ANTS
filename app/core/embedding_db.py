import os
from typing import Optional

from app.embedding_db import setup_database, DatabaseType, BaseDBClient, get_default_connection_string
from app.core.config import config
import logging
logger = logging.getLogger(__name__)
# Global embedding database instance
_embedding_db: Optional[BaseDBClient] = None


def get_embedding_db() -> BaseDBClient:
    """
    Get the global embedding database instance.
    
    Returns:
        Active database client instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    global _embedding_db
    if _embedding_db is None:
        raise RuntimeError("Embedding database not initialized. Call init_embedding_db() first.")
    return _embedding_db


def init_embedding_db() -> None:
    """
    Initialize embedding database on application startup.
    
    This function:
    1. Creates the database file if it doesn't exist
    2. Establishes connection
    3. Creates tables/schema if they don't exist
    """
    global _embedding_db
    
    try:
        # Get connection string using the default path
        db_path = get_default_connection_string(DatabaseType.DUCKDB)
        
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Initialize database with schema creation
        _embedding_db = setup_database(
            db_type=DatabaseType.DUCKDB,
            connection_string=db_path,
            create_schema=True  # This will check and create tables if needed
        )
        
        logger.info(f"Embedding database initialized at {db_path}")
        
    except Exception as e:
        logger.error(f"Failed to initialize embedding database: {str(e)}")
        raise


def close_embedding_db() -> None:
    """Close embedding database connection."""
    global _embedding_db
    if _embedding_db:
        _embedding_db.close()
        _embedding_db = None
        print("Embedding database connection closed")


def check_db_health() -> bool:
    """
    Check if the embedding database is healthy.
    
    Returns:
        True if database is accessible and tables exist
    """
    try:
        db = get_embedding_db()
        # Simple query to check if chunks table exists and is accessible
        result = db.query("SELECT COUNT(*) as count FROM chunks LIMIT 1")
        return True
    except Exception:
        return False