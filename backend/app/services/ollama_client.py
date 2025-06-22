import httpx
import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(
        self,
        app: FastAPI,
        model_name: str = "ALIENTELLIGENCE/mindwell:latest",
        max_history: int = 10,
    ):
        self.model = model_name
        self.max_history = max_history
        self.endpoint = "http://host.docker.internal:11434/api/chat"
        self.redis = app.state.redis
        self.system_msg = (
            "You are Calmindra, an empathetic mental health chatbot. "
            "Your name is Calmindra. You listen actively, validate feelings, "
            "and offer supportive, non-judgmental guidance. Keep responses warm and concise."
        )
        logger.info(f"[OllamaClient] endpoint={self.endpoint!r} model={self.model!r}")

    async def generate(self, user_message: str, session_id: str) -> str:
        key = f"session:{session_id}"
        exists = await self.redis.exists(key)
        if not exists:
            # initialize with system instruction
            await self.redis.rpush(key, f"System: {self.system_msg}")
            await self.redis.expire(key, 86400)

        # append user message
        await self.redis.rpush(key, f"User: {user_message}")

        # retrieve last N messages
        history = await self.redis.lrange(key, -self.max_history, -1)
        # parse into messages list
        messages = []
        for entry in history:
            if entry.startswith("System: "):
                role = "system"
                content = entry[len("System: "):]
            elif entry.startswith("User: "):
                role = "user"
                content = entry[len("User: "):]
            elif entry.startswith("Calmindra: "):
                role = "assistant"
                content = entry[len("Calmindra: "):]
            else:
                # fallback treat as user content
                role = "user"
                content = entry
            messages.append({"role": role, "content": content})

        # send chat request with full history
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()

        # extract assistant reply
        reply = (
            data.get("message", {}).get("content")
            or data.get("response", "")
            or ""
        )

        # append assistant reply
        await self.redis.rpush(key, f"Calmindra: {reply}")
        # trim to keep latest N
        await self.redis.ltrim(key, -self.max_history, -1)
        return reply