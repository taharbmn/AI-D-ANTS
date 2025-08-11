from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.database import engine, Base
from app.models import conversation, message

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create the FastAPI app instance
app = FastAPI(title="FastAPI Chat Application", version="1.0.0")

# Include the API router
app.include_router(api_router, prefix="/api/v1")

# Define a root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Chat Application!"}
