import os
import sys
sys.path.insert(0, 
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
                )
            )
        )
    )
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict
from app.endpoints.router import api_router
from app.core.config import get_settings, init_settings, load_system_prompts, init_client_cache
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
        # Initialize settings and system prompts
        settings = init_settings()
        system_prompts = load_system_prompts()
        
        # Initialize and validate clients
        client_cache = init_client_cache()
        
        logger.info("Application startup complete.")
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

# Create FastAPI app with default values
app = FastAPI(
    title="AI-D-ANTS API",
    description="AI-D-ANTS API for AI-driven data analysis and processing",
    version="0.1.0",
    lifespan=lifespan,
    root_path="/ai"
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