from sqlalchemy.orm import Session
from uuid import UUID
from app.models.message import Message
from app.schemas.message import MessageCreate

def create_message(db: Session, message: MessageCreate) -> Message:
    db_message = Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_message(db: Session, message_id: UUID) -> Message:
    return db.query(Message).filter(Message.id == message_id).first()

def get_messages_by_conversation(db: Session, conversation_id: UUID):
    return db.query(Message).filter(Message.conversation_id == conversation_id).all()

def update_message(db: Session, message_id: UUID, content: str) -> Message:
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db_message.content = content
        db.commit()
        db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: UUID) -> Message:
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message

def delete_messages_by_conversation(db: Session, conversation_id: UUID) -> int:
    """Delete all messages for a conversation and return the count of deleted messages"""
    deleted_count = db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.commit()
    return deleted_count
