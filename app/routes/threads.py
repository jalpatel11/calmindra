import logging
import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth import ProxyIdentity, require_proxy_identity
from app.schemas import ThreadCreate, ThreadResponse, MessageResponse

logger = logging.getLogger(__name__)
router = APIRouter()
SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

@router.get("/", response_model=List[ThreadResponse])
async def list_threads(
    req: Request,
    identity: ProxyIdentity = Depends(require_proxy_identity),
):
    neo4j = req.app.state.neo4j
    try:
        threads = await neo4j.get_threads(identity.user_id)
        return threads
    except Exception:
        logger.exception("Failed to list threads.")
        raise HTTPException(status_code=500, detail="Database error.")

@router.post("/", response_model=ThreadResponse)
async def create_thread(
    req: Request,
    body: ThreadCreate,
    identity: ProxyIdentity = Depends(require_proxy_identity),
):
    if not is_safe_id(body.id):
        raise HTTPException(status_code=400, detail="Invalid thread id.")

    neo4j = req.app.state.neo4j
    try:
        thread = await neo4j.create_thread(identity.user_id, body.id, body.title[:80])
        if not thread:
            raise HTTPException(status_code=403, detail="Thread is unavailable.")
        return thread
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create thread.")
        raise HTTPException(status_code=500, detail="Database error.")

@router.delete("/{thread_id}")
async def delete_thread(
    req: Request,
    thread_id: str,
    identity: ProxyIdentity = Depends(require_proxy_identity),
):
    if not is_safe_id(thread_id):
        raise HTTPException(status_code=400, detail="Invalid thread id.")

    neo4j = req.app.state.neo4j
    try:
        deleted = await neo4j.delete_thread(identity.user_id, thread_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Thread not found.")
        return {"status": "success", "message": "Thread deleted"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to delete thread.")
        raise HTTPException(status_code=500, detail="Database error.")

@router.get("/{thread_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    req: Request,
    thread_id: str,
    identity: ProxyIdentity = Depends(require_proxy_identity),
):
    if not is_safe_id(thread_id):
        raise HTTPException(status_code=400, detail="Invalid thread id.")

    neo4j = req.app.state.neo4j
    try:
        messages = await neo4j.get_messages(identity.user_id, thread_id)
        return messages
    except Exception:
        logger.exception("Failed to get messages.")
        raise HTTPException(status_code=500, detail="Database error.")


def is_safe_id(value: str) -> bool:
    return bool(SAFE_ID_PATTERN.fullmatch(value.strip()))
