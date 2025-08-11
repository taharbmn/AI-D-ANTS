from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.conversation import ConversationCreate, Conversation
from app.crud.conversation import create_conversation, get_conversation, get_conversations, update_conversation, delete_conversation
from app.api.deps import get_db

router = APIRouter()

# @router.post("/", response_model=Conversation)
# def create_new_conversation(conversation: ConversationCreate, db: Session = Depends(get_db)):
#     return create_conversation(db=db, conversation=conversation)

@router.get("/", response_model=list[Conversation])
def read_conversations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    conversations = get_conversations(db=db, skip=skip, limit=limit)
    return conversations

@router.get("/{conversation_id}", response_model=Conversation)
def read_conversation(conversation_id: UUID, db: Session = Depends(get_db)):
    db_conversation = get_conversation(db=db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conversation

@router.put("/{conversation_id}", response_model=Conversation)
def update_existing_conversation(conversation_id: UUID, title: str, db: Session = Depends(get_db)):
    db_conversation = update_conversation(db=db, conversation_id=conversation_id, title=title)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conversation

@router.delete("/{conversation_id}")
def delete_existing_conversation(conversation_id: UUID, db: Session = Depends(get_db)):
    result = delete_conversation(db=db, conversation_id=conversation_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result
