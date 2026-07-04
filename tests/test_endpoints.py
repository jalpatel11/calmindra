from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
TEST_USER_ID = "usr_11111111111111111111111111111111"
TEST_BACKEND_SECRET = "test-backend-secret"
AUTH_HEADERS = {
    "X-User-ID": TEST_USER_ID,
    "X-Backend-Secret": TEST_BACKEND_SECRET,
}

def test_chat_endpoint():
    payload = {
        "user_message": "I'm feeling anxious",
        "session_id": "thread_123"
    }
    response = client.post("/chat/", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "bot_message" in data
    assert data["bot_message"] == "I am Calmindra, how can I help you?"

def test_chat_stream_endpoint():
    payload = {
        "user_message": "I'm feeling anxious",
        "session_id": "thread_123"
    }
    response = client.post("/chat/stream", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.text == "I am Calmindra, streaming now."

def test_rejects_missing_backend_secret():
    payload = {
        "user_message": "I'm feeling anxious",
        "session_id": "thread_123"
    }
    response = client.post("/chat/", json=payload, headers={"X-User-ID": TEST_USER_ID})
    assert response.status_code == 401

def test_ensure_current_user():
    response = client.post("/auth/me", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"id": TEST_USER_ID}

def test_list_threads():
    response = client.get("/threads/", headers=AUTH_HEADERS)
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
    response = client.post("/threads/", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "thread_123"  # returns the mock thread structure

def test_delete_thread():
    response = client.delete("/threads/thread_123", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Thread deleted"}

def test_get_messages():
    response = client.get("/threads/thread_123/messages", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["role"] == "user"
    assert data[0]["content"] == "Hello"
    assert data[1]["role"] == "assistant"
    assert data[1]["content"] == "Hi there"
