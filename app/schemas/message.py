from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class MessageBase(BaseModel):
    content: str
    conversation_id: UUID
    sender_type: Optional[str] = "user"

class MessageCreate(MessageBase):
    pass

class MessageCreateWithConversation(BaseModel):
    content: str
    conversation_id: Optional[UUID] = None

class Message(MessageBase):
    id: UUID
    created_at: datetime
    sender_type: str

    class Config:
        from_attributes = True
