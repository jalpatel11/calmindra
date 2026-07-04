from fastapi import APIRouter, HTTPException, Header, Request, Depends
from typing import Optional
from uuid import uuid4
from app.schemas import ChatRequest, ChatResponse
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

@router.post(
    "/",
    response_model=ChatResponse
)
async def handle_chat(
    req: ChatRequest = Depends(validate_and_rate_limit),
    x_session_id: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header("default_user")
) -> ChatResponse:
    # Resolve session ID (this is the thread ID)
    session_id = x_session_id or req.session_id or str(uuid4())
    
    # Grab services from app state
    neo4j = req.app.state.neo4j
    vertex = req.app.state.vertex
    
    try:
        # Ensure user and thread exist in Neo4j
        await neo4j.create_thread(
            user_id=x_user_id,
            thread_id=session_id,
            title="Chat Conversation"  # Default title, will be updated or set by frontend
        )
        
        # 1. RAG Step: Generate user query embedding
        query_embedding = await vertex.get_embedding(req.user_message)
        
        # 2. RAG Step: Retrieve top 3 documents from Neo4j
        relevant_docs = await neo4j.search_documents(query_embedding, limit=3)
        
        # 3. Assemble RAG system instructions
        context_str = ""
        if relevant_docs:
            context_str = "\n\nHere is relevant therapeutic advice you can draw from:\n---\n"
            context_str += "\n\n".join([doc["content"] for doc in relevant_docs])
            context_str += "\n---\n"
            
        system_instruction = (
            "You are Calmindra, an empathetic, warm, and supportive mental health companion. "
            "Your name is Calmindra. You listen actively, validate feelings, "
            "and offer supportive, non-judgmental guidance. Keep responses warm and concise."
            f"{context_str}"
            "Use the context above to help guide your suggestions and reflections where appropriate, "
            "but answer naturally and conversationally. Do not explicitly say 'According to the context'."
        )
        
        # 4. Fetch conversation history from Neo4j (limit to last 10 messages)
        history = await neo4j.get_messages(session_id)
        # Select last 10
        history = history[-10:]
        
        # 5. Format prompt including chat history
        conversation = ""
        for msg in history:
            role_label = "User" if msg["role"] == "user" else "Calmindra"
            conversation += f"{role_label}: {msg['content']}\n\n"
        conversation += f"User: {req.user_message}\n\nCalmindra:"
        
        # 6. Save user message to Neo4j
        user_msg_id = str(uuid4())
        await neo4j.save_message(
            thread_id=session_id,
            message_id=user_msg_id,
            role="user",
            content=req.user_message
        )
        
        # 7. Generate bot reply using Google Vertex AI (Gemini)
        reply = await vertex.generate_completion(
            prompt=conversation,
            system_instruction=system_instruction
        )
        reply = reply.strip()
        
        # 8. Save bot reply to Neo4j
        bot_msg_id = str(uuid4())
        await neo4j.save_message(
            thread_id=session_id,
            message_id=bot_msg_id,
            role="assistant",
            content=reply
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"AI/Database execution error: {e}")
        
    return ChatResponse(bot_message=reply)