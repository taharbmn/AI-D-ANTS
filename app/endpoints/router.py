from fastapi import APIRouter
from app.endpoints import anomalies, metadata, chat

api_router = APIRouter()

api_router.include_router(
    anomalies.router,
    prefix="/anomalies"
)

api_router.include_router(
    metadata.router, 
    prefix="/metadata"
)

api_router.include_router(
    chat.router, 
    prefix="/chat"
)