from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional, List
from app.schemas import ThreadCreate, ThreadResponse, MessageResponse

router = APIRouter()

@router.get("/", response_model=List[ThreadResponse])
async def list_threads(
    req: Request,
    x_user_id: Optional[str] = Header("default_user")
):
    neo4j = req.app.state.neo4j
    try:
        threads = await neo4j.get_threads(x_user_id)
        return threads
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/", response_model=ThreadResponse)
async def create_thread(
    req: Request,
    body: ThreadCreate,
    x_user_id: Optional[str] = Header("default_user")
):
    neo4j = req.app.state.neo4j
    try:
        thread = await neo4j.create_thread(x_user_id, body.id, body.title)
        if not thread:
            raise HTTPException(status_code=400, detail="Could not create thread")
        return thread
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{thread_id}")
async def delete_thread(
    req: Request,
    thread_id: str
):
    neo4j = req.app.state.neo4j
    try:
        await neo4j.delete_thread(thread_id)
        return {"status": "success", "message": "Thread deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{thread_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    req: Request,
    thread_id: str
):
    neo4j = req.app.state.neo4j
    try:
        messages = await neo4j.get_messages(thread_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
