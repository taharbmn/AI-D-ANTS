from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.message import MessageCreate, Message, MessageCreateWithConversation
from app.schemas.conversation import ConversationCreate, Conversation
from app.crud.message import create_message, get_messages_by_conversation, get_message, update_message, delete_message
from app.crud.conversation import create_conversation, get_conversation
from app.api.deps import get_db

router = APIRouter()

@router.post("/", response_model=dict)
def create_conversation_with_first_message(
    message_data: MessageCreateWithConversation,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation using the first message, or add message to existing conversation.
    If conversation_id is provided and exists, add message to that conversation.
    If conversation_id is not provided or doesn't exist, create a new conversation.
    The conversation title will be the first 20 characters of the message content.
    """
    existing_conversation = None

    # Check if conversation_id is provided and if the conversation exists
    if message_data.conversation_id:
        existing_conversation = get_conversation(db=db, conversation_id=message_data.conversation_id)

    if existing_conversation:
        # Use existing conversation
        conversation = existing_conversation

        # Create the message with the existing conversation ID
        message_create = MessageCreate(
            content=message_data.content,
            conversation_id=conversation.id
        )
        new_message = create_message(db=db, message=message_create)

        return {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at
            },
            "message": {
                "id": new_message.id,
                "content": new_message.content,
                "conversation_id": new_message.conversation_id,
                "created_at": new_message.created_at
            },
            "action": "added_to_existing_conversation"
        }
    else:
        # Create new conversation
        # Extract first 20 characters for the title
        title = message_data.content[:20]
        if len(message_data.content) > 20:
            title += "..."

        # Create the conversation first
        conversation_create = ConversationCreate(title=title)
        new_conversation = create_conversation(db=db, conversation=conversation_create)

        # Create the first message with the conversation ID
        message_create = MessageCreate(
            content=message_data.content,
            conversation_id=new_conversation.id
        )
        new_message = create_message(db=db, message=message_create)

        return {
            "conversation": {
                "id": new_conversation.id,
                "title": new_conversation.title,
                "created_at": new_conversation.created_at,
                "updated_at": new_conversation.updated_at
            },
            "message": {
                "id": new_message.id,
                "content": new_message.content,
                "conversation_id": new_message.conversation_id,
                "created_at": new_message.created_at
            },
            "action": "created_new_conversation"
        }


@router.get("/conversation/{conversation_id}", response_model=list[Message])
def read_messages_by_conversation(conversation_id: UUID, db: Session = Depends(get_db)):
    messages = get_messages_by_conversation(db=db, conversation_id=conversation_id)
    return messages

