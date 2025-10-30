"""
Routes API pour la gestion des documents RAG
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])


# ============================================================================
# Models
# ============================================================================

class DocumentUploadRequest(BaseModel):
    """Requête pour uploader un document"""
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict)
    collection_name: str = "documents"


class DocumentUploadResponse(BaseModel):
    """Réponse après upload de document"""
    doc_id: str
    filename: str
    format: str
    chunks_created: int
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    metadata: Dict[str, str]


class DirectoryLoadRequest(BaseModel):
    """Requête pour charger un répertoire de documents"""
    directory_path: str
    collection_name: str = "documents"
    recursive: bool = True
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict)


class DirectoryLoadResponse(BaseModel):
    """Réponse après chargement de répertoire"""
    files_processed: int
    files_succeeded: int
    files_failed: int
    results: Dict[str, Any]


class SearchRequest(BaseModel):
    """Requête de recherche améliorée"""
    query: str
    top_k: int = 5
    collection_name: str = "documents"
    filters: Optional[Dict[str, str]] = None
    use_cache: bool = True
    enable_reranking: bool = False


class SearchResult(BaseModel):
    """Résultat de recherche"""
    doc_id: str
    chunk_id: str
    content: str
    score: float
    metadata: Dict[str, str]


class SearchResponse(BaseModel):
    """Réponse de recherche"""
    results: List[SearchResult]
    total_matches: int
    from_cache: bool = False
    cache_stats: Optional[Dict] = None


class CacheStatsResponse(BaseModel):
    """Statistiques du cache"""
    size: int
    max_size: int
    hits: int
    misses: int
    hit_rate: float
    evictions: int
    expirations: int
    total_requests: int


# ============================================================================
# Routes
# ============================================================================

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = None,
    collection_name: str = "documents"
):
    """
    Upload et indexe un document.

    Supporte: PDF, DOCX, TXT, MD, HTML
    """
    try:
        # Parser métadonnées JSON si fourni
        import json
        meta = json.loads(metadata) if metadata else {}

        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Importer les services (lazy import pour éviter circular dependency)
            from services.document_parser import DocumentParserService
            from services.ollama import OllamaService
            from services.vector_store import VectorStoreService
            from agents.rag.indexer import RAGIndexerAgent
            from agents.rag.document_loader import RAGDocumentLoaderAgent
            from models.agent import AgentExecutionRequest

            # Initialiser les services
            parser = DocumentParserService()
            ollama = OllamaService()
            vector_store = VectorStoreService()
            indexer = RAGIndexerAgent(ollama, vector_store)
            loader = RAGDocumentLoaderAgent(parser, indexer)

            # Charger le document
            request = AgentExecutionRequest(
                agent_id="document_loader",
                input={
                    "file_path": tmp_path,
                    "doc_id": Path(file.filename).stem,
                    "metadata": {**meta, "filename": file.filename},
                    "collection_name": collection_name,
                }
            )

            result = await loader.execute(request)

            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)

            return DocumentUploadResponse(
                doc_id=result.output["doc_id"],
                filename=file.filename,
                format=result.output["format"],
                chunks_created=result.output["chunks_created"],
                word_count=result.output.get("word_count"),
                page_count=result.output.get("page_count"),
                metadata=result.output["metadata"]
            )

        finally:
            # Nettoyer le fichier temporaire
            Path(tmp_path).unlink(missing_ok=True)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Métadonnées JSON invalides")
    except Exception as e:
        logger.error(f"Erreur upload document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-directory", response_model=DirectoryLoadResponse)
async def load_directory(
    payload: DirectoryLoadRequest,
    background_tasks: BackgroundTasks
):
    """
    Charge tous les documents d'un répertoire.

    Traite les fichiers en background si nombreux.
    """
    try:
        from services.document_parser import DocumentParserService
        from services.ollama import OllamaService
        from services.vector_store import VectorStoreService
        from agents.rag.indexer import RAGIndexerAgent
        from agents.rag.document_loader import RAGDocumentLoaderAgent

        # Initialiser les services
        parser = DocumentParserService()
        ollama = OllamaService()
        vector_store = VectorStoreService()
        indexer = RAGIndexerAgent(ollama, vector_store)
        loader = RAGDocumentLoaderAgent(parser, indexer)

        # Charger le répertoire
        results = await loader.load_directory(
            directory_path=payload.directory_path,
            collection_name=payload.collection_name,
            recursive=payload.recursive,
            metadata=payload.metadata
        )

        # Compter succès/échecs
        succeeded = sum(1 for r in results.values() if r.success)
        failed = len(results) - succeeded

        return DirectoryLoadResponse(
            files_processed=len(results),
            files_succeeded=succeeded,
            files_failed=failed,
            results={path: {"success": r.success, "error": r.error} for path, r in results.items()}
        )

    except Exception as e:
        logger.error(f"Erreur chargement répertoire: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_documents(payload: SearchRequest):
    """
    Recherche sémantique dans les documents indexés.

    Options:
    - Cache automatique des résultats
    - Reranking optionnel pour meilleure pertinence
    """
    try:
        from services.ollama import OllamaService
        from services.vector_store import VectorStoreService
        from services.search_cache import SearchCacheService
        from agents.rag.cached_searcher import RAGCachedSearcherAgent
        from agents.rag.reranker import RAGRerankerAgent
        from models.agent import AgentExecutionRequest

        # Initialiser les services
        ollama = OllamaService()
        vector_store = VectorStoreService()
        cache = SearchCacheService()

        # Searcher avec cache
        searcher = RAGCachedSearcherAgent(
            ollama_service=ollama,
            vector_store=vector_store,
            cache=cache,
            enable_cache=payload.use_cache
        )

        # Recherche
        search_request = AgentExecutionRequest(
            agent_id="cached_searcher",
            input={
                "query": payload.query,
                "top_k": payload.top_k,
                "filters": payload.filters or {},
                "use_cache": payload.use_cache,
            }
        )

        result = await searcher.execute(search_request)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        search_results = result.output.get("results", [])

        # Reranking optionnel
        if payload.enable_reranking and search_results:
            reranker = RAGRerankerAgent(ollama)

            rerank_request = AgentExecutionRequest(
                agent_id="reranker",
                input={
                    "query": payload.query,
                    "results": search_results,
                    "top_k": payload.top_k,
                }
            )

            rerank_result = await reranker.execute(rerank_request)

            if rerank_result.success:
                search_results = rerank_result.output.get("reranked_results", search_results)

        # Formater les résultats
        formatted_results = [
            SearchResult(
                doc_id=r.get("doc_id", ""),
                chunk_id=r.get("chunk_id", r.get("id", "")),
                content=r.get("content", ""),
                score=r.get("final_score", r.get("score", 0.0)),
                metadata=r.get("metadata", {})
            )
            for r in search_results
        ]

        return SearchResponse(
            results=formatted_results,
            total_matches=len(formatted_results),
            from_cache=result.output.get("from_cache", False),
            cache_stats=result.output.get("cache_stats")
        )

    except Exception as e:
        logger.error(f"Erreur recherche: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """Retourne les statistiques du cache de recherche"""
    try:
        from services.search_cache import SearchCacheService

        cache = SearchCacheService()
        stats = cache.get_stats()

        return CacheStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Erreur récupération stats cache: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache():
    """Vide complètement le cache de recherche"""
    try:
        from services.search_cache import SearchCacheService

        cache = SearchCacheService()
        count = cache.clear()

        return {"message": f"Cache vidé: {count} entrées supprimées", "count": count}

    except Exception as e:
        logger.error(f"Erreur vidage cache: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/cleanup")
async def cleanup_cache():
    """Nettoie les entrées expirées du cache"""
    try:
        from services.search_cache import SearchCacheService

        cache = SearchCacheService()
        count = cache.cleanup_expired()

        return {"message": f"Nettoyage terminé: {count} entrées expirées supprimées", "count": count}

    except Exception as e:
        logger.error(f"Erreur nettoyage cache: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def get_supported_formats():
    """Liste les formats de documents supportés"""
    try:
        from services.document_parser import DocumentParserService

        parser = DocumentParserService()
        extensions = parser.get_supported_extensions()

        return {
            "supported_extensions": extensions,
            "count": len(extensions),
            "formats": ["PDF", "DOCX", "TXT", "Markdown", "HTML"]
        }

    except Exception as e:
        logger.error(f"Erreur récupération formats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
