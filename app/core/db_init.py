"""
Database initialization utilities
"""
import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def run_migrations():
    """Run Alembic migrations to ensure database is up to date"""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        
        # Set environment variables for Alembic
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        
        # Run alembic upgrade head
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info("Database migrations completed successfully")
            if result.stdout:
                logger.info(f"Migration output: {result.stdout}")
        else:
            logger.error(f"Migration failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Migration error: {result.stderr}")
            if result.stdout:
                logger.info(f"Migration output: {result.stdout}")
            raise RuntimeError(f"Database migration failed: {result.stderr}")
            
    except FileNotFoundError:
        logger.error("Alembic not found. Please ensure it's installed and in PATH")
        raise
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise

def init_database():
    """Initialize database by running migrations"""
    logger.info("Initializing database...")
    run_migrations()
    logger.info("Database initialization completed")
