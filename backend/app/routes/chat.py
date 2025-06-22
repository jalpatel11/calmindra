from fastapi import APIRouter, HTTPException, Header, Request, Depends
from typing import Optional
from uuid import uuid4
from app.schemas import ChatRequest, ChatResponse
from app.services.ollama_client import OllamaClient

router = APIRouter()

# Validation and rate limiting dependency
async def validate_and_rate_limit(
    req: Request,
    body: ChatRequest
) -> ChatRequest:
    text = body.user_message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if len(text) > 500:
        raise HTTPException(status_code=413, detail="Message too long; limit to 500 characters.")

    # Simple in-memory rate limiting per IP: 5 req/min
    client_ip = req.client.host
    store = req.app.state._rate_limit_store
    now = req.app.state._time_func()
    timestamps = [ts for ts in store.get(client_ip, []) if now - ts < 60]
    if len(timestamps) >= 5:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    timestamps.append(now)
    store[client_ip] = timestamps

    return body

# Dependency to provide Redis-backed Ollama client
async def get_client(request: Request) -> OllamaClient:
    return OllamaClient(request.app)

@router.post(
    "/",
    response_model=ChatResponse
)
async def handle_chat(
    req: ChatRequest = Depends(validate_and_rate_limit),
    x_session_id: Optional[str] = Header(None),
    client: OllamaClient = Depends(get_client)
) -> ChatResponse:
    # Resolve session ID
    session_id = x_session_id or req.session_id or str(uuid4())
    try:
        reply = await client.generate(req.user_message, session_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")
    return ChatResponse(bot_message=reply)