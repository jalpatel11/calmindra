import logging
from fastapi import FastAPI
from redis.asyncio import Redis
from app.routes.chat import router as chat_router
import time

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Calmindra Backend",
    description="Mental-health chatbot with Redis-persisted sessions",
)

@app.on_event("startup")
async def startup_event():
    # Redis client
    app.state.redis = Redis.from_url(
        "redis://redis:6379", encoding="utf-8", decode_responses=True
    )
    # simple in-memory rate-limit store
    app.state._rate_limit_store = {}
    app.state._time_func = time.time

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()

app.include_router(chat_router, prefix="/chat", tags=["chat"])
