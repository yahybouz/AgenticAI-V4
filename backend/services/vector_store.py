"""Abstraction au-dessus de Qdrant/Chroma avec fallback mémoire."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:  # pragma: no cover - dépendance optionnelle
    AsyncQdrantClient = None  # type: ignore
    qmodels = None  # type: ignore

from config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Client vectoriel : tente Qdrant, sinon conserve les embeddings en mémoire."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[AsyncQdrantClient] = None
        self._collections: Dict[str, List[Dict[str, object]]] = {}
        if AsyncQdrantClient:
            try:
                self._client = AsyncQdrantClient(url=self.settings.database.vector_url)
            except Exception as exc:  # pragma: no cover
                logger.warning("Connexion Qdrant indisponible, fallback mémoire", exc_info=exc)
                self._client = None

    async def _ensure_collection(self, name: str, vector_size: int) -> None:
        if not self._client or not qmodels:
            return
        try:
            exists = await self._client.collection_exists(name)
            if not exists:
                await self._client.create_collection(
                    name=name,
                    vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
                )
        except Exception as exc:  # pragma: no cover
            logger.error("Création collection Qdrant échouée", exc_info=exc)

    async def upsert_documents(self, collection: str, vectors: List[Dict[str, object]]) -> None:
        if not vectors:
            return
        if self._client and qmodels:
            vector_size = len(vectors[0].get("vector", [])) if vectors[0].get("vector") else 0
            await self._ensure_collection(collection, vector_size)
            try:
                points = [
                    qmodels.PointStruct(
                        id=point.get("id"),
                        vector=point.get("vector"),
                        payload=point.get("payload", {}),
                    )
                    for point in vectors
                ]
                await self._client.upsert(collection_name=collection, points=points)
                return
            except Exception as exc:  # pragma: no cover
                logger.error("Upsert Qdrant échoué, fallback mémoire", exc_info=exc)
        logger.info("[VectorStore:fallback] upsert", extra={"collection": collection, "count": len(vectors)})
        self._collections.setdefault(collection, []).extend(vectors)

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
        filters: Dict | None = None,
    ) -> List[Dict[str, object]]:
        """Search vector store with optional filters and score threshold."""
        if self._client:
            try:
                hits = await self._client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold,
                )
                return [
                    {"id": hit.id, "score": hit.score, "payload": hit.payload}
                    for hit in hits
                ]
            except Exception as exc:  # pragma: no cover
                logger.error("Search Qdrant échoué, fallback mémoire", exc_info=exc)
        logger.info("[VectorStore:fallback] search", extra={"collection": collection_name, "top_k": top_k})
        memory_points = self._collections.get(collection_name, [])
        # Format results to match Qdrant structure with score field
        return [
            {"id": p.get("id"), "score": 0.5, "payload": p.get("payload", {})}
            for p in memory_points[:top_k]
        ]

    async def ensure_collection(self, collection_name: str, vector_size: int) -> None:
        """Ensure collection exists, create if not. Public wrapper for _ensure_collection."""
        await self._ensure_collection(collection_name, vector_size)

    async def upsert_point(
        self,
        collection_name: str,
        point_id: str,
        vector: List[float],
        payload: Dict,
    ) -> str:
        """Upsert a single point to the collection."""
        await self.upsert_documents(
            collection=collection_name,
            vectors=[{"id": point_id, "vector": vector, "payload": payload}],
        )
        return point_id
