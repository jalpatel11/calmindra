import os
import logging
from typing import AsyncIterator
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class VertexClient:
    def __init__(self):
        # google-genai client automatically picks up GEMINI_API_KEY from environment if present.
        # It can also fall back to default Google Cloud credentials in Vertex AI environment.
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.info("GEMINI_API_KEY not found in env. Initializing genai.Client with GCP environment credentials.")
            self.client = genai.Client()
            
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
        logger.info(f"[VertexClient] Initialized with model={self.model}, embedding_model={self.embedding_model}")

    async def generate_completion(self, prompt: str, system_instruction: str = None) -> str:
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self._completion_config(system_instruction),
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Error in VertexClient generate_completion: {e}")
            raise e

    async def stream_completion(
        self, prompt: str, system_instruction: str = None
    ) -> AsyncIterator[str]:
        try:
            stream = await self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=self._completion_config(system_instruction),
            )
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Error in VertexClient stream_completion: {e}")
            raise e

    async def get_embedding(self, text: str) -> list[float]:
        try:
            config = types.EmbedContentConfig(output_dimensionality=768)
            response = await self.client.aio.models.embed_content(
                model=self.embedding_model,
                contents=text,
                config=config,
            )
            if response and response.embeddings:
                return response.embeddings[0].values
            raise ValueError("No embeddings returned by Vertex AI API.")
        except Exception as e:
            logger.error(f"Error in VertexClient get_embedding: {e}")
            raise e

    def _completion_config(self, system_instruction: str = None):
        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
