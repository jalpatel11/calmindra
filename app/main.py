import os
import logging
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.routes.chat import router as chat_router
from app.routes.threads import router as threads_router
from app.services.neo4j_client import Neo4jClient
from app.services.vertex_client import VertexClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Calmindra Backend",
    description="Privacy-first mental health chatbot with Cloud RAG & Neo4j",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Rate limiting in-memory fallback store
    app.state._rate_limit_store = {}
    app.state._time_func = time.time

    # 1. Initialize Redis connection
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        logger.info(f"Connecting to Redis at: {redis_url}")
        app.state.redis = Redis.from_url(
            redis_url, encoding="utf-8", decode_responses=True
        )
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}. Fallback to memory will be used.")
    
    # 2. Initialize Neo4j Client & Index
    try:
        logger.info("Initializing Neo4j Client...")
        app.state.neo4j = Neo4jClient()
        await app.state.neo4j.initialize_database()
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j database: {e}. Graph functionality will fail until configured.")
    
    # 3. Initialize Vertex AI Client (Gemini + Embeddings)
    try:
        logger.info("Initializing Vertex AI Client...")
        app.state.vertex = VertexClient()
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI client: {e}. Completions will fail until configured.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down resources...")
    # Close Redis
    if hasattr(app.state, "redis"):
        await app.state.redis.close()
    
    # Close Neo4j driver
    if hasattr(app.state, "neo4j"):
        await app.state.neo4j.close()

# Include routes
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(threads_router, prefix="/threads", tags=["threads"])
