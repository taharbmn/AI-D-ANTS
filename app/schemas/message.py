from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    conversation_id: str
    sender_type: Optional[str] = "user"

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
