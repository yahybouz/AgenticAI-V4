"""
RAG Cached Searcher - Version améliorée du searcher avec cache intégré
"""

import logging
from typing import Optional

from models.agent import AgentExecutionRequest, AgentExecutionResult
from services.ollama import OllamaService
from services.vector_store import VectorStoreService
from services.search_cache import SearchCacheService
from agents.rag.searcher import RAGSearcherAgent

logger = logging.getLogger(__name__)


class RAGCachedSearcherAgent:
    """
    Searcher RAG avec cache LRU intégré.

    Améliore les performances en cachant les résultats des recherches fréquentes.
    """

    def __init__(
        self,
        ollama_service: OllamaService,
        vector_store: VectorStoreService,
        cache: Optional[SearchCacheService] = None,
        top_k: int = 5,
        score_threshold: float = 0.7,
        enable_cache: bool = True,
    ):
        """
        Args:
            ollama_service: Service Ollama pour embeddings
            vector_store: Service vector store
            cache: Service de cache (créé automatiquement si None)
            top_k: Nombre de résultats par défaut
            score_threshold: Score minimum de pertinence
            enable_cache: Activer/désactiver le cache
        """
        self.searcher = RAGSearcherAgent(
            ollama_service=ollama_service,
            vector_store=vector_store,
            top_k=top_k,
            score_threshold=score_threshold
        )

        self.cache = cache or SearchCacheService(max_size=1000, default_ttl=3600)
        self.enable_cache = enable_cache
        self.name = "RAG Cached Searcher"
        self.description = "Recherche sémantique avec cache LRU pour meilleures performances"

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        """
        Execute semantic search avec cache.

        Args:
            request.input doit contenir:
                - query: Question de recherche
                - top_k: Nombre de résultats (optionnel)
                - filters: Filtres de métadonnées (optionnel)
                - use_cache: Forcer utilisation cache (optionnel, défaut: True)
                - cache_ttl: TTL custom pour cette requête (optionnel)

        Returns:
            AgentExecutionResult avec résultats de recherche
        """
        query = request.input.get("query", "")
        top_k = request.input.get("top_k", self.searcher.top_k)
        filters = request.input.get("filters", {})
        use_cache = request.input.get("use_cache", True)
        cache_ttl = request.input.get("cache_ttl")

        if not query:
            return AgentExecutionResult(
                success=False,
                output={},
                error="query requis"
            )

        # Paramètres de cache
        cache_key_params = {
            "top_k": top_k,
            "filters": str(sorted(filters.items())) if filters else "",
            "collection": self.searcher.collection_name,
        }

        # Tentative de récupération depuis le cache
        if self.enable_cache and use_cache:
            cached_result = self.cache.get(query, **cache_key_params)

            if cached_result is not None:
                logger.info(f"[RAGCachedSearcher] Cache HIT: {query[:50]}...")

                # Ajouter métadonnée indiquant que c'est depuis le cache
                cached_result["output"]["from_cache"] = True
                cached_result["output"]["cache_stats"] = self.cache.get_stats()

                return AgentExecutionResult(**cached_result)

        logger.info(f"[RAGCachedSearcher] Cache MISS: {query[:50]}...")

        # Exécuter la recherche via le searcher standard
        result = await self.searcher.execute(request)

        # Mettre en cache si succès et cache activé
        if result.success and self.enable_cache:
            # Convertir le résultat en dict pour le cache
            result_dict = {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "citations": result.citations,
            }

            self.cache.set(query, result_dict, ttl=cache_ttl, **cache_key_params)
            logger.debug(f"[RAGCachedSearcher] Résultat mis en cache")

        # Ajouter métadonnée indiquant que ce n'est pas depuis le cache
        result.output["from_cache"] = False
        result.output["cache_stats"] = self.cache.get_stats()

        return result

    def invalidate_cache(self, query: str, **kwargs):
        """
        Invalide une entrée spécifique du cache.

        Args:
            query: Requête à invalider
            **kwargs: Paramètres de recherche (top_k, filters, etc.)
        """
        self.cache.invalidate(query, **kwargs)
        logger.info(f"[RAGCachedSearcher] Cache invalidé pour: {query[:50]}...")

    def clear_cache(self) -> int:
        """
        Vide complètement le cache.

        Returns:
            Nombre d'entrées supprimées
        """
        count = self.cache.clear()
        logger.info(f"[RAGCachedSearcher] Cache vidé: {count} entrées")
        return count

    def cleanup_expired(self) -> int:
        """
        Nettoie les entrées expirées du cache.

        Returns:
            Nombre d'entrées expirées supprimées
        """
        return self.cache.cleanup_expired()

    def get_cache_stats(self) -> dict:
        """
        Retourne les statistiques d'utilisation du cache.

        Returns:
            Dict avec statistiques (hits, misses, hit_rate, etc.)
        """
        return self.cache.get_stats()
