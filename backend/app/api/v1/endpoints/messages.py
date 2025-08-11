from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any, Optional
from app.schemas.message import MessageCreate, Message, MessageCreateWithConversation
from app.schemas.conversation import ConversationCreate, Conversation
from app.crud.message import create_message, get_messages_by_conversation, get_message, update_message, delete_message, get_last_messages
from app.crud.conversation import create_conversation, get_conversation
from app.core.database import get_db

router = APIRouter()

def get_conversation_context(
    conversation_id: Optional[UUID],
    db: Session,
    message_count: int = 10
) -> List[Dict[str, Any]]:
    """
    Get conversation context (previous messages) for a given conversation.
    Returns only the specified number of most recent messages, not all conversation.

    Args:
        conversation_id: The UUID of the conversation (can be None)
        db: Database session
        message_count: Number of recent messages to retrieve (default: 10)

    Returns:
        List of message items formatted for conversation context (limited to message_count)
    """
    if conversation_id is None:
        return []

    # Use the optimized database query to get only the last N messages
    previous_messages = get_last_messages(db=db, conversation_id=conversation_id, count=message_count)

    if not previous_messages:
        return []

    # Convert to message items format
    messages_historical = []
    for msg in previous_messages:
        content = []

        # Add text content only if it exists
        if msg.content and msg.content.strip():
            content.append({"text": msg.content})

        message_item = {
            "role": "user" if msg.sender_type == "user" else "assistant",
            "content": content
        }
        messages_historical.append(message_item)

    # Print conversation context for debugging (uncomment if needed)
    # for msg in messages_historical:
    #     content_text = msg["content"][0]["text"] if msg["content"] else ""
    #     print(f"Role: {msg['role']}, Content: {content_text}")

    return messages_historical

def get_last_messages_formatted(
    conversation_id: Optional[UUID],
    db: Session,
    count: int = 10
) -> List[Dict[str, Any]]:
    """
    Récupère les derniers messages de la conversation actuelle dans le format demandé.

    Args:
        conversation_id: The UUID of the conversation (can be None)
        db: Database session
        count: Number of recent messages to retrieve (default: 10)

    Returns:
        List of formatted messages ready for conversation context
    """
    if conversation_id is None:
        return []

    # Récupère les messages bruts du repository avec la nouvelle fonction optimisée
    raw_messages = get_last_messages(db=db, conversation_id=conversation_id, count=count)

    if not raw_messages:
        return []

    # Transforme chaque message dans le format demandé
    formatted_messages = []
    for msg in raw_messages:
        message = {
            "role": "user" if msg.sender_type == "user" else "assistant",
            "content": [{"text": msg.content}] if msg.content and msg.content.strip() else []
        }
        formatted_messages.append(message)

    return formatted_messages

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
        if not existing_conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    if existing_conversation:
        # Use existing conversation
        conversation = existing_conversation

        # Create the message with the existing conversation ID
        message_create = MessageCreate(
            content=message_data.content,
            conversation_id=conversation.id
        )
        new_message = create_message(db=db, message=message_create)

        # Get conversation history
        conversation_history = get_conversation_context(
            conversation_id=conversation.id,
            db=db,
            message_count=10
        )

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
            "conversation_history": conversation_history,
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

        # Get conversation history
        conversation_history = get_conversation_context(
            conversation_id=new_conversation.id,
            db=db,
            message_count=10
        )

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
            "conversation_history": conversation_history,
            "action": "created_new_conversation"
        }


@router.get("/conversation/{conversation_id}", response_model=list[Message])
def read_messages_by_conversation(conversation_id: UUID, db: Session = Depends(get_db)):
    messages = get_messages_by_conversation(db=db, conversation_id=conversation_id)
    return messages


@router.get("/conversation/{conversation_id}/context")
def get_conversation_context_endpoint(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    message_count: int = 10
):
    """
    Get conversation context (formatted for AI/chat systems) for a given conversation.
    Returns the last N messages in a format suitable for conversation history.
    """
    context = get_conversation_context(
        conversation_id=conversation_id,
        db=db,
        message_count=message_count
    )

    return {
        "conversation_id": conversation_id,
        "message_count": len(context),
        "context": context
    }

