"""RAG.Searcher Agent - Hybrid search with vector similarity and keyword matching."""
from __future__ import annotations

from typing import Any, Dict, List

from models import AgentExecutionRequest, AgentExecutionResult
from services.ollama import OllamaService
from services.vector_store import VectorStoreService


class SearchResult:
    """Represents a search result with score and metadata."""

    def __init__(
        self,
        content: str,
        score: float,
        doc_id: str,
        chunk_index: int,
        metadata: Dict[str, Any],
    ):
        self.content = content
        self.score = score
        self.doc_id = doc_id
        self.chunk_index = chunk_index
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "content": self.content,
            "score": self.score,
            "doc_id": self.doc_id,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
        }


class RAGSearcherAgent:
    """
    Agent responsible for searching indexed documents.

    Capabilities:
    - Semantic search using vector similarity
    - Keyword filtering
    - Result ranking and deduplication
    - Citation extraction
    """

    def __init__(
        self,
        ollama_service: OllamaService,
        vector_store: VectorStoreService,
        top_k: int = 5,
        score_threshold: float = 0.7,
    ):
        self.ollama = ollama_service
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.collection_name = "documents"

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        """
        Execute semantic search.

        Input payload:
        - query: str - Search query
        - top_k: int (optional) - Number of results to return
        - filters: dict (optional) - Metadata filters (e.g., {"doc_id": "doc123"})

        Returns:
        - results: list[SearchResult]
        - query_embedding_model: str
        - total_matches: int
        """
        query = request.payload.get("query", "")
        top_k = request.payload.get("top_k", self.top_k)
        filters = request.payload.get("filters", {})

        if not query:
            return AgentExecutionResult(
                success=False,
                output={},
                error="No query provided for search",
            )

        try:
            # 1. Generate query embedding
            query_embedding = await self.ollama.generate_embedding(
                text=query,
                model="nomic-embed-text:latest",
            )

            # 2. Search vector store
            search_results = await self.vector_store.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                top_k=top_k,
                score_threshold=self.score_threshold,
                filters=filters,
            )

            # 3. Convert to SearchResult objects
            results = []
            for result in search_results:
                search_result = SearchResult(
                    content=result["payload"]["content"],
                    score=result["score"],
                    doc_id=result["payload"]["doc_id"],
                    chunk_index=result["payload"]["chunk_index"],
                    metadata={
                        k: v
                        for k, v in result["payload"].items()
                        if k not in ["content", "doc_id", "chunk_index"]
                    },
                )
                results.append(search_result)

            # 4. Deduplicate by doc_id (keep highest scoring chunk per doc)
            deduplicated = self._deduplicate_results(results)

            return AgentExecutionResult(
                success=True,
                output={
                    "results": [r.to_dict() for r in deduplicated],
                    "query_embedding_model": "nomic-embed-text:latest",
                    "total_matches": len(deduplicated),
                },
                error=None,
            )

        except Exception as e:
            return AgentExecutionResult(
                success=False,
                output={},
                error=f"Search failed: {str(e)}",
            )

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Deduplicate results by doc_id, keeping the highest scoring chunk.

        This prevents the same document from appearing multiple times
        when multiple chunks match the query.
        """
        seen_docs: Dict[str, SearchResult] = {}

        for result in results:
            doc_id = result.doc_id
            if doc_id not in seen_docs or result.score > seen_docs[doc_id].score:
                seen_docs[doc_id] = result

        # Return sorted by score
        return sorted(seen_docs.values(), key=lambda x: x.score, reverse=True)


async def create_rag_searcher_agent(
    ollama_service: OllamaService,
    vector_store: VectorStoreService,
) -> RAGSearcherAgent:
    """Factory function to create RAG.Searcher agent."""
    return RAGSearcherAgent(
        ollama_service=ollama_service,
        vector_store=vector_store,
        top_k=5,
        score_threshold=0.7,
    )
