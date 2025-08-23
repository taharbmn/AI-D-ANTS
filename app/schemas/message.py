from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    conversation_id: str
    sender_type: Optional[str] = "user"
    # Allow sources and codes lists to contain either dictionaries (future extensibility)
    # or plain strings (current usage: file paths for sources, code snippets for codes)
    sources: Optional[List[Union[str, Dict[str, Any]]]] = None
    codes: Optional[List[Union[str, Dict[str, Any]]]] = None

class MessageCreate(MessageBase):
    pass

class MessageCreateWithConversation(BaseModel):
    content: str
    conversation_id: Optional[str] = None
    available_datasets: Optional[list[str]] = None

class Message(MessageBase):
    id: str
    created_at: datetime
    sender_type: str

    class Config:
        from_attributes = True
