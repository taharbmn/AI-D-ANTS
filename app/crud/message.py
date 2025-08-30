from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Tuple
from app.models.message import Message
from app.schemas.message import MessageCreate

def create_message(db: Session, message: MessageCreate) -> Message:
    db_message = Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_message(db: Session, message_id: str) -> Message:
    return db.query(Message).filter(Message.id == message_id).first()

def get_messages_by_conversation(db: Session, conversation_id: str):
    return db.query(Message).filter(Message.conversation_id == conversation_id).all()

def get_messages_by_conversation_paginated(
    db: Session,
    conversation_id: str,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[Message], int]:
    """Return a page of messages for a conversation and the total count.

    Args:
        db: DB session
        conversation_id: conversation id
        skip: number of rows to skip (offset)
        limit: max number of rows to return

    Returns:
        (messages, total_count)
    """
    # Total count
    total = db.query(func.count(Message.id)).filter(Message.conversation_id == conversation_id).scalar() or 0

    # Page of messages ordered chronologically (oldest first)
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return messages, total

def get_last_messages(db: Session, conversation_id: str, count: int = 10) -> List[Message]:
    """
    Get the last N messages from a specific conversation, ordered by timestamp descending (most recent first),
    then sorted chronologically for proper conversation flow.
    """
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(count).all()

    # Return messages sorted chronologically (oldest first) for proper conversation flow
    return sorted(messages, key=lambda m: m.created_at)

def update_message(db: Session, message_id: str, content: str) -> Message:
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db_message.content = content
        db.commit()
        db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: str) -> Message:
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message

def delete_messages_by_conversation(db: Session, conversation_id: str) -> int:
    """Delete all messages for a conversation and return the count of deleted messages"""
    deleted_count = db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.commit()
    return deleted_count
