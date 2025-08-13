from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class MessageBase(BaseModel):
    content: str
    sender_type: Optional[str] = "user"

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: UUID
    conversation_id: UUID
    sender_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []

    class Config:
        from_attributes = True
