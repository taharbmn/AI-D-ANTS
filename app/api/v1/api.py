from fastapi import APIRouter
from app.api.v1.endpoints import conversations, messages, env_variables

api_routerr = APIRouter()

api_routerr.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_routerr.include_router(messages.router, prefix="/messages", tags=["messages"])
api_routerr.include_router(env_variables.router, prefix="/env", tags=["environment-variables"])
