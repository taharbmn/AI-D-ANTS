from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.core.database import Base

class Message(Base):
    __tablename__ = 'messages'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    content = Column(String, nullable=False)
    sender_type = Column(String, nullable=False, default="user")
    conversation_id = Column(String, ForeignKey('conversations.id', ondelete="CASCADE"), nullable=False)
    sources = Column(JSON, nullable=True)
    codes = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")
