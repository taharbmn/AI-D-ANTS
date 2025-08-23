from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict
from app.endpoints.router import api_router
from app.core.config import initialize_config, load_system_prompts, initialize_cache_client
from app.core.local_ollama_init import configure_ollama_by_capacity
from app.core.embedding_db import init_embedding_db, close_embedding_db
from app.core.db_init import init_database
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up application...")
    try:
        # Initialize database (run migrations)
        init_database()
        configure_ollama_by_capacity()

        # Initialize settings and system prompts
        config = initialize_config()
        system_prompts = load_system_prompts()

        # Initialize and validate clients
        client_cache = initialize_cache_client()

        # Initialize embedding database
        init_embedding_db()

        logger.info("loaded system prompts: %s", len(system_prompts))
        logger.info("Application startup complete with config: %s", config)
        logger.info("Client cache initialized with clients: %s", client_cache)
        logger.info("Application startup complete.")
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    
    # Close embedding database connection
    close_embedding_db()

# Create FastAPI app with default values
app = FastAPI(
    title="AI-D-ANTS API",
    description="AI-D-ANTS API for AI-driven data analysis and processing",
    version="0.1.0",
    lifespan=lifespan
    # root_path="/ai"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint - redirects to docs"""
    return {
            "message": "Welcome to AI-D-ANTS",
            "version": "0.1.0",
            "docs_url": "/docs"
        }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""

    return {"status": "healthy", "version": "0.1.0"}
