from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate

def create_conversation(db: Session, conversation: ConversationCreate) -> Conversation:
    db_conversation = Conversation(**conversation.dict())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: str) -> Conversation:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_conversations(db: Session, skip: int = 0, limit: int = 10) -> list[Conversation]:
    return db.query(Conversation).offset(skip).limit(limit).all()

def update_conversation(db: Session, conversation_id: str, title: str) -> Conversation:
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db_conversation.title = title
        db.commit()
        db.refresh(db_conversation)
    return db_conversation

def delete_conversation(db: Session, conversation_id: str) -> bool:
    """
    Delete a conversation. Related messages will be automatically deleted due to CASCADE constraint.
    """
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
        return True
    return False
