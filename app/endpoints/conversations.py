from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.conversation import Conversation, ConversationCreate
from app.schemas.message import Message as FullMessage
from app.crud.conversation import create_conversation, get_conversation, get_conversations, update_conversation, delete_conversation
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=Conversation)
def create_new_conversation(conversation: ConversationCreate, db: Session = Depends(get_db)):
    return create_conversation(db=db, conversation=conversation)

@router.get("/", response_model=list[Conversation])
def read_conversations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    conversations = get_conversations(db, skip=skip, limit=limit)
    return conversations

@router.get("/{conversation_id}", response_model=dict)
def read_conversation(conversation_id: str, db: Session = Depends(get_db)):
    db_conversation = get_conversation(db, conversation_id=conversation_id)
    if not db_conversation:
        # Pas de check 404 demandé, on retourne juste null
        return None

    msgs = getattr(db_conversation, 'messages', []) or []
    messages_payload = [
        {
            'id': m.id,
            'content': m.content,
            'sender_type': m.sender_type,
            'conversation_id': m.conversation_id,
            'sources': m.sources,  # peut être null
            'codes': m.codes,      # peut être null
            'table_data': m.table_data,  # peut être null
            'charts': m.charts,    # peut être null
            'created_at': m.created_at
        }
        for m in msgs
    ]

    return {
        'id': db_conversation.id,
        'title': db_conversation.title,
        'created_at': db_conversation.created_at,
        'updated_at': db_conversation.updated_at,
        'messages': messages_payload
    }

@router.put("/{conversation_id}")
def update_existing_conversation(conversation_id: str, title: str, db: Session = Depends(get_db)):
    updated_conversation = update_conversation(db, conversation_id, title)
    if updated_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return updated_conversation

@router.delete("/{conversation_id}")
def delete_existing_conversation(conversation_id: str, db: Session = Depends(get_db)):
    success = delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}
