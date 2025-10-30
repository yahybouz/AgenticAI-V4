"""RAG.Indexer Agent - Document chunking and embedding generation."""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from models import AgentExecutionRequest, AgentExecutionResult
from services.ollama import OllamaService
from services.vector_store import VectorStoreService


class DocumentChunk:
    """Represents a chunk of a document with metadata."""

    def __init__(
        self,
        content: str,
        doc_id: str,
        chunk_index: int,
        metadata: Dict[str, Any] | None = None,
    ):
        self.content = content
        self.doc_id = doc_id
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
        self.chunk_id = self._generate_chunk_id()

    def _generate_chunk_id(self) -> str:
        """Generate unique ID for this chunk."""
        raw = f"{self.doc_id}:{self.chunk_index}:{self.content[:50]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class RAGIndexerAgent:
    """
    Agent responsible for indexing documents into the vector store.

    Capabilities:
    - Split documents into semantic chunks
    - Generate embeddings using Ollama
    - Store chunks in Qdrant vector store
    - Handle metadata and provenance
    """

    def __init__(
        self,
        ollama_service: OllamaService,
        vector_store: VectorStoreService,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
    ):
        self.ollama = ollama_service
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.collection_name = "documents"

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        """
        Execute document indexing.

        Input payload:
        - content: str - Document content to index
        - doc_id: str - Unique document identifier
        - metadata: dict - Optional metadata (source, author, date, etc.)

        Returns:
        - chunks_created: int
        - chunk_ids: list[str]
        - embedding_model: str
        """
        content = request.payload.get("content", "")
        doc_id = request.payload.get("doc_id", "unknown")
        metadata = request.payload.get("metadata", {})

        if not content:
            return AgentExecutionResult(
                success=False,
                output={},
                error="No content provided for indexing",
            )

        try:
            # 1. Split document into chunks
            chunks = self._chunk_document(content, doc_id, metadata)

            # 2. Generate embeddings for each chunk
            chunk_ids = []
            for chunk in chunks:
                embedding = await self.ollama.generate_embedding(
                    text=chunk.content,
                    model="nomic-embed-text:latest",
                )

                # 3. Store in vector store
                point_id = await self.vector_store.upsert_point(
                    collection_name=self.collection_name,
                    point_id=chunk.chunk_id,
                    vector=embedding,
                    payload={
                        "content": chunk.content,
                        "doc_id": chunk.doc_id,
                        "chunk_index": chunk.chunk_index,
                        **chunk.metadata,
                    },
                )
                chunk_ids.append(point_id)

            return AgentExecutionResult(
                success=True,
                output={
                    "chunks_created": len(chunks),
                    "chunk_ids": chunk_ids,
                    "embedding_model": "nomic-embed-text:latest",
                    "doc_id": doc_id,
                },
                error=None,
            )

        except Exception as e:
            return AgentExecutionResult(
                success=False,
                output={},
                error=f"Indexing failed: {str(e)}",
            )

    def _chunk_document(
        self, content: str, doc_id: str, metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Split document into overlapping chunks.

        Strategy: Simple sliding window with character-based chunking.
        Future: Use sentence boundaries, paragraph detection, etc.
        """
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(content):
            end = start + self.chunk_size
            chunk_content = content[start:end]

            # Avoid breaking words - find last space
            if end < len(content):
                last_space = chunk_content.rfind(" ")
                if last_space > 0:
                    chunk_content = chunk_content[:last_space]
                    end = start + last_space

            chunk = DocumentChunk(
                content=chunk_content.strip(),
                doc_id=doc_id,
                chunk_index=chunk_index,
                metadata=metadata,
            )
            chunks.append(chunk)

            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            chunk_index += 1

        return chunks


async def create_rag_indexer_agent(
    ollama_service: OllamaService,
    vector_store: VectorStoreService,
) -> RAGIndexerAgent:
    """Factory function to create RAG.Indexer agent."""
    agent = RAGIndexerAgent(
        ollama_service=ollama_service,
        vector_store=vector_store,
        chunk_size=512,
        chunk_overlap=128,
    )

    # Ensure collection exists
    await vector_store.ensure_collection(
        collection_name="documents",
        vector_size=768,  # nomic-embed-text dimension
    )

    return agent
