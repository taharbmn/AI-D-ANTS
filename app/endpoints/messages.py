from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.schemas.message import MessageCreate, Message, MessageCreateWithConversation
from app.schemas.conversation import ConversationCreate, Conversation
from app.crud.message import create_message, get_messages_by_conversation, get_message, update_message, delete_message, get_last_messages
from app.crud.conversation import create_conversation, get_conversation
from app.core.database import get_db
from app.models.chat import ChatRequest, ChatMessage
from app.endpoints.chat import chat_endpoint

router = APIRouter()

def get_conversation_context(
    conversation_id: Optional[str],
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
    conversation_id: Optional[str],
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
async def create_conversation_with_first_message(
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
    conversation_history = []

    # Check if conversation_id is provided and if the conversation exists
    if message_data.conversation_id:
        existing_conversation = get_conversation(db=db, conversation_id=message_data.conversation_id)
        if not existing_conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get conversation history only if conversation exists
        conversation_history = get_conversation_context(
            conversation_id=existing_conversation.id,
            db=db,
            message_count=10
        )

    if existing_conversation:
        # Use existing conversation
        conversation = existing_conversation

        # Create the message with the existing conversation ID
        message_create = MessageCreate(
            content=message_data.content,
            conversation_id=conversation.id
        )
        new_message = create_message(db=db, message=message_create)
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

        # Set conversation for consistency
        conversation = new_conversation

        # Prepare chat request (for new conversation, history will be empty)
    chat_request = ChatRequest(
            message=ChatMessage(
                role="user",
                content=message_data.content
            ),
            messages_historical=[
                ChatMessage(
                    role=msg["role"],
                    content=msg["content"][0]["text"] if msg["content"] and len(msg["content"]) > 0 else ""
                )
                for msg in conversation_history
            ],
            available_datasets=message_data.available_datasets
        )

    # Send to chat endpoint
    chat_response = await chat_endpoint(chat_request)

    # Extract assistant response
    if chat_response.get("success") and chat_response.get("response", {}).get("messages"):
        try:
            # Handle different response formats
            messages = chat_response["response"]["messages"]
            if messages and len(messages) > 0:
                first_message = messages[0]
                
                # Check if first_message is a dict or string
                if isinstance(first_message, dict):
                    # Check if content is a list or string
                    if isinstance(first_message.get("content"), list):
                        # Content is a list
                        content_list = first_message["content"]
                        if content_list and len(content_list) > 0:
                            assistant_message_content = content_list[0].get("text", "")
                        else:
                            assistant_message_content = ""
                    elif isinstance(first_message.get("content"), str):
                        # Content is a string
                        assistant_message_content = first_message["content"]
                    else:
                        assistant_message_content = str(first_message.get("content", ""))
                elif isinstance(first_message, str):
                    # The entire message is a string
                    assistant_message_content = first_message
                else:
                    assistant_message_content = str(first_message)
                
                sources = chat_response.get("sources", [])
                codes = chat_response.get("codes", [])
                table_data = chat_response.get("table_data", [])
                charts = chat_response.get("charts", [])
            else:
                assistant_message_content = "No response from assistant"
                sources = []
                codes = []
                table_data = []
                charts = []

            # Save assistant response to database
            assistant_message = MessageCreate(
                content=assistant_message_content,
                conversation_id=conversation.id,
                sender_type="assistant"
            )
            assistant_db_message = create_message(db=db, message=assistant_message)

            return {
                "message": {
                    "id": assistant_db_message.id,
                    "content": assistant_db_message.content,
                    "sources": sources,
                    "codes": codes,
                    "table_data": table_data,
                    "charts": charts,
                    "conversation_id": assistant_db_message.conversation_id,
                    "created_at": assistant_db_message.created_at
                }
            }
        except (KeyError, IndexError, TypeError, AttributeError) as e:
            # Log the error and the response structure for debugging
            import logging
            logging.error(f"Error parsing chat response: {e}")
            logging.error(f"Chat response structure: {chat_response}")
            
            # Save a fallback message
            assistant_message = MessageCreate(
                content="Error processing assistant response",
                conversation_id=conversation.id,
                sender_type="assistant"
            )
            assistant_db_message = create_message(db=db, message=assistant_message)
            
            return {
                "message": {
                    "id": assistant_db_message.id,
                    "content": assistant_db_message.content,
                    "sources": [],
                    "codes": [],
                    "table_data": [],
                    "charts": [],
                    "conversation_id": assistant_db_message.conversation_id,
                    "created_at": assistant_db_message.created_at
                },
                "error": f"Error parsing response: {str(e)}"
            }
    else:
        # Handle chat error
        return {
            "error": "Failed to get chat response",
            "chat_response": chat_response
        }



@router.get("/conversation/{conversation_id}", response_model=list[Message])
def read_messages_by_conversation(conversation_id: str, db: Session = Depends(get_db)):
    messages = get_messages_by_conversation(db=db, conversation_id=conversation_id)
    return messages

