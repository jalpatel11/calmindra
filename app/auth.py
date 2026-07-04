import hmac
import os
import re
from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException, status


USER_ID_PATTERN = re.compile(r"^usr_[a-f0-9]{32,64}$", re.IGNORECASE)


@dataclass(frozen=True)
class ProxyIdentity:
    user_id: str


async def require_proxy_identity(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_backend_secret: Optional[str] = Header(None, alias="X-Backend-Secret"),
) -> ProxyIdentity:
    expected_secret = os.getenv("BACKEND_API_SECRET")

    if not expected_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Backend proxy authentication is not configured.",
        )

    if not x_backend_secret or not hmac.compare_digest(x_backend_secret, expected_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if not x_user_id or not USER_ID_PATTERN.fullmatch(x_user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return ProxyIdentity(user_id=x_user_id)
