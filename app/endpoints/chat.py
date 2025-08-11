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
import json
import logging
from fastapi import APIRouter
from dotenv import load_dotenv
from app.models.chat import ChatRequest

router = APIRouter()

load_dotenv()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for user messages
    """
    # Process the chat request
    response = process_chat_request(request)
    return response