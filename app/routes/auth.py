import logging
import hashlib
import secrets
import hmac
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from app.auth import ProxyIdentity, require_proxy_identity, require_backend_secret
from app.schemas import UserResponse, CredentialsAuthRequest

logger = logging.getLogger(__name__)
router = APIRouter()

def hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = secrets.token_bytes(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"pbkdf2_sha256$100000${salt.hex()}${pwd_hash.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        parts = stored_hash.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        original_hash = bytes.fromhex(parts[3])
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return hmac.compare_digest(pwd_hash, original_hash)
    except Exception:
        return False

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

@router.post("/signup", response_model=UserResponse)
async def signup(
    request: Request,
    body: CredentialsAuthRequest,
    _secret: None = Depends(require_backend_secret)
) -> UserResponse:
    neo4j = request.app.state.neo4j
    email = body.email.strip().lower()
    password = body.password
    
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
        
    try:
        existing_user = await neo4j.get_user_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
            
        # Generate user_id compliant with pattern ^usr_[a-f0-9]{32,64}$
        user_uuid = uuid4().hex
        user_id = f"usr_{user_uuid}"
        
        pwd_hash = hash_password(password)
        created = await neo4j.create_credentials_user(user_id, email, pwd_hash)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create user.")
            
        return UserResponse(id=created["id"])
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to register user.")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/login", response_model=UserResponse)
async def login(
    request: Request,
    body: CredentialsAuthRequest,
    _secret: None = Depends(require_backend_secret)
) -> UserResponse:
    neo4j = request.app.state.neo4j
    email = body.email.strip().lower()
    password = body.password
    
    try:
        user = await neo4j.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
            
        stored_hash = user.get("passwordHash")
        if not stored_hash or not verify_password(password, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
            
        return UserResponse(id=user["id"])
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to authenticate user.")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
