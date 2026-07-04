import logging
import re
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.auth import ProxyIdentity, require_proxy_identity
from app.schemas import ChatRequest, ChatResponse


logger = logging.getLogger(__name__)
router = APIRouter()

MAX_MESSAGE_LENGTH = 500
SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


@dataclass(frozen=True)
class ChatContext:
    session_id: str
    prompt: str
    system_instruction: str
    neo4j: object
    vertex: object


async def validate_and_rate_limit(
    request: Request,
    body: ChatRequest,
    identity: ProxyIdentity = Depends(require_proxy_identity),
) -> ChatRequest:
    text = body.user_message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if len(text) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=413,
            detail="Message too long; limit to 500 characters.",
        )

    body.user_message = text

    # Simple fallback rate limit per authenticated user and client IP: 5 req/min.
    client_ip = request.client.host if request.client else "unknown"
    store = getattr(request.app.state, "_rate_limit_store", None)
    if store is None:
        store = {}
        request.app.state._rate_limit_store = store

    now = request.app.state._time_func()
    rate_key = f"{identity.user_id}:{client_ip}"
    timestamps = [ts for ts in store.get(rate_key, []) if now - ts < 60]
    if len(timestamps) >= 5:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    timestamps.append(now)
    store[rate_key] = timestamps

    return body


@router.post("/", response_model=ChatResponse)
async def handle_chat(
    request: Request,
    req: ChatRequest = Depends(validate_and_rate_limit),
    identity: ProxyIdentity = Depends(require_proxy_identity),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
) -> ChatResponse:
    session_id = resolve_session_id(x_session_id, req.session_id)

    try:
        context = await build_chat_context(request, req, identity, session_id)
        reply = await context.vertex.generate_completion(
            prompt=context.prompt,
            system_instruction=context.system_instruction,
        )
        reply = (reply or "").strip() or "I am here with you. Could you tell me a little more?"

        await context.neo4j.save_message(
            identity.user_id,
            context.session_id,
            str(uuid4()),
            "assistant",
            reply,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Chat completion failed.")
        raise HTTPException(status_code=502, detail="AI or database execution failed.")

    return ChatResponse(bot_message=reply)


@router.post("/stream")
async def handle_chat_stream(
    request: Request,
    req: ChatRequest = Depends(validate_and_rate_limit),
    identity: ProxyIdentity = Depends(require_proxy_identity),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
) -> StreamingResponse:
    session_id = resolve_session_id(x_session_id, req.session_id)
    context = await build_chat_context(request, req, identity, session_id)

    return StreamingResponse(
        stream_assistant_reply(context, identity),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "X-Session-ID": context.session_id,
        },
    )


def resolve_session_id(header_session_id: Optional[str], body_session_id: Optional[str]) -> str:
    raw_session_id = header_session_id or body_session_id
    if raw_session_id is None:
        return str(uuid4())

    session_id = raw_session_id.strip()
    if not SAFE_ID_PATTERN.fullmatch(session_id):
        raise HTTPException(status_code=400, detail="Invalid session id.")

    return session_id


async def build_chat_context(
    request: Request,
    req: ChatRequest,
    identity: ProxyIdentity,
    session_id: str,
) -> ChatContext:
    neo4j = request.app.state.neo4j
    vertex = request.app.state.vertex

    thread = await neo4j.create_thread(
        user_id=identity.user_id,
        thread_id=session_id,
        title="Chat Conversation",
    )
    if not thread:
        raise HTTPException(status_code=403, detail="Thread is unavailable.")

    query_embedding = await vertex.get_embedding(req.user_message)
    relevant_docs = await neo4j.search_documents(query_embedding, limit=3)

    context_str = ""
    if relevant_docs:
        context_str = "\n\nRelevant supportive context:\n---\n"
        context_str += "\n\n".join(
            str(doc.get("content", ""))[:2000]
            for doc in relevant_docs
            if doc.get("content")
        )
        context_str += "\n---\n"

    system_instruction = (
        "You are Calmindra, an empathetic, warm, and supportive mental health companion. "
        "You listen actively, validate feelings, and offer supportive, non-judgmental guidance. "
        "Keep responses warm, concise, and practical. "
        "You are not a crisis service; if someone may be in immediate danger, encourage emergency "
        "services or a trusted local crisis line right away. "
        f"{context_str}"
        "Use the context to guide suggestions where appropriate, but answer naturally and do not "
        "say 'according to the context'."
    )

    history = await neo4j.get_messages(identity.user_id, session_id)
    history = history[-10:]

    conversation = ""
    for msg in history:
        role_label = "User" if msg["role"] == "user" else "Calmindra"
        conversation += f"{role_label}: {msg['content']}\n\n"
    conversation += f"User: {req.user_message}\n\nCalmindra:"

    saved_message = await neo4j.save_message(
        identity.user_id,
        session_id,
        str(uuid4()),
        "user",
        req.user_message,
    )
    if not saved_message:
        raise HTTPException(status_code=404, detail="Thread not found.")

    return ChatContext(
        session_id=session_id,
        prompt=conversation,
        system_instruction=system_instruction,
        neo4j=neo4j,
        vertex=vertex,
    )


async def stream_assistant_reply(context: ChatContext, identity: ProxyIdentity):
    chunks: list[str] = []

    try:
        async for delta in context.vertex.stream_completion(
            prompt=context.prompt,
            system_instruction=context.system_instruction,
        ):
            if delta:
                chunks.append(delta)
                yield delta

        reply = "".join(chunks).strip()
        if not reply:
            reply = "I am here with you. Could you tell me a little more?"
            yield reply

        await context.neo4j.save_message(
            identity.user_id,
            context.session_id,
            str(uuid4()),
            "assistant",
            reply,
        )
    except Exception:
        logger.exception("Streaming chat completion failed.")
        if not chunks:
            yield "I could not reach Calmindra just now. Please try again in a moment."
