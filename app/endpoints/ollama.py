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
from typing import List, Dict, Any, Optional
import re
import time
import json
import logging
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import time

load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("pull_ollama_model")
async def pull_ollama_model(model_name: str):
    logger.info(f"Pulling Ollama model: {model_name}")
    try:
        # Simulate pulling the model (replace with actual implementation)
        time.sleep(2)
        logger.info(f"Successfully pulled Ollama model: {model_name}")
        return JSONResponse(
            status_code=200,
            content={
                "response": f"Model {model_name} pulled successfully",
                "success": True,
                "status": 200
            }
        )
    except Exception as e:
        logger.error(f"Failed to pull Ollama model: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "response": "Failed to pull Ollama model",
                "success": False,
                "status": 500
            }
        )
