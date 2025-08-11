from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Pydantic models for request/response validation
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: str = Field(..., description="ID of the conversation to fetch message history from")

class ChatResponse(BaseModel):
    role: str = Field(..., description="Response role (assistant)")
    content: str = Field(..., description="Response content")
    model: Optional[str] = Field(None, description="Model used for generation")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")
    stop_reason: Optional[str] = Field(None, description="Reason for stopping generation")


class MetaDataRequest(BaseModel):
    filepath: str


class DataRequest(BaseModel):
    data_source_file: str = Field(..., description="S3 path to the data file")
    message: ChatMessage = Field(..., description="User message with question about the data")

class AnalyzeRequest(BaseModel):
    """
        {
            "destination": "",
            "sources": {
                "local-data://Category/Product_Catgories.csv": {
                    "destination": "local-data://my-result.json",
                    "max_depth"  : None
                }
            }
        }
    """
    destination: str = Field(..., description="Destination path for the analysis result")
    sources: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Dictionary of source files with their destination and max depth for analysis"
    )