from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.database import engine, Base
from app.core.config import settings
from app.models import conversation, message

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create the FastAPI app instance
app = FastAPI(title="FastAPI Chat Application", version="1.0.0")

# Configure CORS
if settings.DEBUG:
    # In development, allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False when allow_origins=["*"]
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("CORS configured for development - allowing all origins")
else:
    # In production, use specific origins
    allowed_origins = settings.ALLOWED_HOSTS.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print(f"CORS configured for production - allowed origins: {allowed_origins}")

# Include the API router
app.include_router(api_router, prefix="/api/v1")

# Define a root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Chat Application!"}
