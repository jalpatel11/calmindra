import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth import ProxyIdentity, require_proxy_identity
from app.schemas import UserResponse


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/me", response_model=UserResponse)
async def ensure_current_user(
    request: Request,
    identity: ProxyIdentity = Depends(require_proxy_identity),
) -> UserResponse:
    try:
        await request.app.state.neo4j.create_user(identity.user_id)
    except Exception:
        logger.exception("Failed to ensure authenticated user.")
        raise HTTPException(status_code=500, detail="Database error.")

    return UserResponse(id=identity.user_id)
