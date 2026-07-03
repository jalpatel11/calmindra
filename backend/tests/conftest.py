import pytest
from unittest.mock import AsyncMock, MagicMock
from app.main import app as fastapi_app

@pytest.fixture
def mock_neo4j():
    client = MagicMock()
    client.initialize_database = AsyncMock()
    client.create_user = AsyncMock(return_value="test_user")
    client.create_thread = AsyncMock(return_value={
        "id": "thread_123", 
        "title": "Test Thread", 
        "createdAt": "2026-07-03T12:00:00Z"
    })
    client.get_threads = AsyncMock(return_value=[{
        "id": "thread_123", 
        "title": "Test Thread", 
        "createdAt": "2026-07-03T12:00:00Z"
    }])
    client.delete_thread = AsyncMock()
    client.get_messages = AsyncMock(return_value=[
        {"id": "msg_1", "role": "user", "content": "Hello", "createdAt": "2026-07-03T12:00:00Z"},
        {"id": "msg_2", "role": "assistant", "content": "Hi there", "createdAt": "2026-07-03T12:01:00Z"}
    ])
    client.save_message = AsyncMock(return_value={
        "id": "msg_new", 
        "role": "user", 
        "content": "New Message", 
        "createdAt": "2026-07-03T12:02:00Z"
    })
    client.search_documents = AsyncMock(return_value=[{
        "content": "Title: Calmness\nContent: Breathe deeply.", 
        "score": 0.95
    }])
    client.close = AsyncMock()
    return client

@pytest.fixture
def mock_vertex():
    client = MagicMock()
    client.get_embedding = AsyncMock(return_value=[0.1] * 768)
    client.generate_completion = AsyncMock(return_value="I am Calmindra, how can I help you?")
    return client

@pytest.fixture(autouse=True)
def setup_app_state(mock_neo4j, mock_vertex):
    # Inject our mocked clients to fastapi app.state to bypass network lookups during tests
    fastapi_app.state.neo4j = mock_neo4j
    fastapi_app.state.vertex = mock_vertex
    fastapi_app.state.redis = MagicMock()
    fastapi_app.state.redis.close = AsyncMock()
    fastapi_app.state._rate_limit_store = {}
    fastapi_app.state._time_func = lambda: 1000.0
