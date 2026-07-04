from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint():
    payload = {
        "user_message": "I'm feeling anxious",
        "session_id": "thread_123"
    }
    response = client.post("/chat/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "bot_message" in data
    assert data["bot_message"] == "I am Calmindra, how can I help you?"

def test_list_threads():
    response = client.get("/threads/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "thread_123"
    assert data[0]["title"] == "Test Thread"

def test_create_thread():
    payload = {
        "id": "thread_new",
        "title": "New Session"
    }
    response = client.post("/threads/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "thread_123"  # returns the mock thread structure

def test_delete_thread():
    response = client.delete("/threads/thread_123")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Thread deleted"}

def test_get_messages():
    response = client.get("/threads/thread_123/messages")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["role"] == "user"
    assert data[0]["content"] == "Hello"
    assert data[1]["role"] == "assistant"
    assert data[1]["content"] == "Hi there"
