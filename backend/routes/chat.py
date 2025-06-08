from fastapi import APIRouter, HTTPException
from backend.models import ChatRequest
from backend.services.generate import generate_response

router = APIRouter()

@router.post("/chat/")
async def chat_handler(payload: ChatRequest):
    try:
        print("Received:", payload.message)
        reply = generate_response(payload.message)
        return {"response": reply}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
