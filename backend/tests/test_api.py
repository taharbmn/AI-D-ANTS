from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_conversations():
    response = client.get("/api/v1/conversations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_conversation():
    response = client.post("/api/v1/conversations/", json={"title": "New Conversation"})
    assert response.status_code == 201
    assert "id" in response.json()

def test_create_conversation_with_first_message():
    """Test the new endpoint that creates a conversation from the first message"""
    test_content = "This is a test message content for creating a new conversation"
    response = client.post("/api/v1/messages/create-conversation", json={"content": test_content})

    assert response.status_code == 200
    data = response.json()

    # Check that both conversation and message are returned
    assert "conversation" in data
    assert "message" in data
    assert "action" in data
    assert data["action"] == "created_new_conversation"

    # Check conversation properties
    conversation = data["conversation"]
    assert "id" in conversation
    assert "title" in conversation
    assert "created_at" in conversation
    assert "updated_at" in conversation

    # Check that title is first 20 characters + "..." if content is longer
    expected_title = test_content[:20] + "..."
    assert conversation["title"] == expected_title

    # Check message properties
    message = data["message"]
    assert "id" in message
    assert "content" in message
    assert "conversation_id" in message
    assert "created_at" in message
    assert message["content"] == test_content
    assert message["conversation_id"] == conversation["id"]

def test_create_conversation_with_short_message():
    """Test creating conversation with message shorter than 20 characters"""
    test_content = "Short message"
    response = client.post("/api/v1/messages/create-conversation", json={"content": test_content})

    assert response.status_code == 200
    data = response.json()

    # Title should be exactly the content without "..." since it's shorter than 20 chars
    conversation = data["conversation"]
    assert conversation["title"] == test_content
    assert data["action"] == "created_new_conversation"

def test_add_message_to_existing_conversation():
    """Test adding a message to an existing conversation"""
    # First create a conversation
    first_message = "This is the first message"
    response1 = client.post("/api/v1/messages/create-conversation", json={"content": first_message})
    assert response1.status_code == 200

    conversation_id = response1.json()["conversation"]["id"]

    # Now add a second message to the same conversation
    second_message = "This is the second message"
    response2 = client.post("/api/v1/messages/create-conversation", json={
        "content": second_message,
        "conversation_id": conversation_id
    })

    assert response2.status_code == 200
    data = response2.json()

    # Should use existing conversation
    assert data["action"] == "added_to_existing_conversation"
    assert data["conversation"]["id"] == conversation_id
    assert data["message"]["content"] == second_message
    assert data["message"]["conversation_id"] == conversation_id

def test_invalid_conversation_id_creates_new():
    """Test that providing an invalid conversation_id creates a new conversation"""
    import uuid
    invalid_id = str(uuid.uuid4())
    test_content = "Message with invalid conversation ID"

    response = client.post("/api/v1/messages/create-conversation", json={
        "content": test_content,
        "conversation_id": invalid_id
    })

    assert response.status_code == 200
    data = response.json()

    # Should create new conversation since the provided ID doesn't exist
    assert data["action"] == "created_new_conversation"
    assert data["conversation"]["id"] != invalid_id

def test_get_messages():
    response = client.get("/api/v1/messages/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_message():
    response = client.post("/api/v1/messages/", json={"conversation_id": 1, "content": "Hello!"})
    assert response.status_code == 201
    assert "id" in response.json()

def test_delete_conversation_with_messages():
    """Test that deleting a conversation also deletes all related messages"""
    # Create a conversation with multiple messages
    test_content = "This is the first message in conversation"
    response1 = client.post("/api/v1/messages/create-conversation", json={"content": test_content})
    assert response1.status_code == 200

    conversation_id = response1.json()["conversation"]["id"]

    # Add more messages to the conversation
    for i in range(3):
        message_content = f"Additional message {i+1}"
        response = client.post("/api/v1/messages/create-conversation", json={
            "content": message_content,
            "conversation_id": conversation_id
        })
        assert response.status_code == 200

    # Verify we have messages in the conversation
    messages_response = client.get(f"/api/v1/messages/conversation/{conversation_id}")
    assert messages_response.status_code == 200
    messages = messages_response.json()
    assert len(messages) == 4  # 1 initial + 3 additional

    # Delete the conversation
    delete_response = client.delete(f"/api/v1/conversations/{conversation_id}")
    assert delete_response.status_code == 200

    delete_data = delete_response.json()
    assert delete_data["success"] is True
    assert delete_data["deleted_messages_count"] == 4
    assert "deleted successfully" in delete_data["message"]

    # Verify conversation is deleted
    get_response = client.get(f"/api/v1/conversations/{conversation_id}")
    assert get_response.status_code == 404

    # Verify messages are also deleted
    messages_response_after = client.get(f"/api/v1/messages/conversation/{conversation_id}")
    assert messages_response_after.status_code == 200
    assert len(messages_response_after.json()) == 0
