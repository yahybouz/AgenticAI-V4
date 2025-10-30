"""Wrapper around le runtime Ollama local."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from config import get_settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Client asynchrone vers Ollama avec repli local."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> Optional[httpx.AsyncClient]:
        if self._client is None:
            try:
                self._client = httpx.AsyncClient(
                    base_url=self.settings.ollama_base_url,
                    timeout=self.settings.ollama_timeout_seconds,
                )
            except Exception as exc:  # pragma: no cover
                logger.warning("Impossible d'initialiser le client Ollama", exc_info=exc)
        return self._client

    async def chat(self, prompt: str, model: str | None = None, **kwargs: Any) -> Dict[str, Any]:
        model_name = model or self.settings.ollama_models[0].name
        payload = {"model": model_name, "prompt": prompt} | kwargs
        client = await self._get_client()
        if client:
            try:
                response = await client.post("/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                output = data.get("response") or data.get("output") or ""
                return {"model": model_name, "output": output, "raw": data}
            except httpx.HTTPError as exc:
                logger.warning("Ollama chat HTTPError", exc_info=exc)
        logger.info("[Ollama:fallback] chat", extra={"model": model_name})
        return {"model": model_name, "output": f"Stub response for: {prompt[:64]}"}

    async def embed(self, texts: List[str]) -> List[List[float]]:
        embedding_model = next((m for m in self.settings.ollama_models if m.role == "embedding"), None)
        if not embedding_model:
            return []
        client = await self._get_client()
        payload = {"model": embedding_model.name, "input": texts}
        if client:
            try:
                response = await client.post("/api/embeddings", json=payload)
                response.raise_for_status()
                data = response.json()
                vectors = data.get("embeddings") or data.get("data") or []
                return [vec.get("embedding", []) if isinstance(vec, dict) else vec for vec in vectors]
            except httpx.HTTPError as exc:
                logger.warning("Ollama embeddings HTTPError", exc_info=exc)
        logger.info("[Ollama:fallback] embeddings", extra={"count": len(texts)})
        return [[0.0 for _ in range(8)] for _ in texts]

    async def generate_embedding(self, text: str, model: str | None = None) -> List[float]:
        """Generate embedding for a single text. Helper method for RAG agents."""
        embeddings = await self.embed([text])
        return embeddings[0] if embeddings else []

    async def transcribe(self, audio_bytes: bytes, language: str | None = None) -> Dict[str, Any]:
        asr_model = next((m for m in self.settings.ollama_models if m.role == "asr"), None)
        if not asr_model:
            return {"text": "", "language": language or "auto", "model": ""}
        client = await self._get_client()
        if client:
            files = {"file": ("audio.wav", audio_bytes)}
            data = {"model": asr_model.name}
            if language:
                data["language"] = language
            try:
                response = await client.post("/api/audio/transcriptions", files=files, data=data)
                response.raise_for_status()
                payload = response.json()
                return {
                    "text": payload.get("text", ""),
                    "language": payload.get("language", language or "auto"),
                    "model": asr_model.name,
                }
            except httpx.HTTPError as exc:
                logger.warning("Ollama transcription HTTPError", exc_info=exc)
        logger.info("[Ollama:fallback] transcribe", extra={"language": language or "auto"})
        return {"text": "", "language": language or "auto", "model": asr_model.name}
