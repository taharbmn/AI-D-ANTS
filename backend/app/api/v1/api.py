from fastapi import APIRouter
from app.api.v1.endpoints import conversations, messages, env_variables

api_router = APIRouter()

api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(env_variables.router, prefix="/env", tags=["environment-variables"])
