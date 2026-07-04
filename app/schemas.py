from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    user_message: str = Field(..., example="I've been feeling anxious.")
    session_id: Optional[str] = Field(None, example="session123")

class ChatResponse(BaseModel):
    bot_message: str = Field(..., example="I'm here to listen. What’s on your mind?")

class ThreadCreate(BaseModel):
    id: str = Field(..., example="thread_123")
    title: str = Field(..., example="New Chat Thread")

class ThreadResponse(BaseModel):
    id: str
    title: str
    createdAt: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    createdAt: str

class UserResponse(BaseModel):
    id: str
