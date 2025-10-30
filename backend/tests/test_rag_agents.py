"""Tests for RAG agents (Indexer, Searcher, Citation)."""
import pytest

from agents.rag import RAGCitationAgent, RAGIndexerAgent, RAGSearcherAgent
from models import AgentExecutionRequest
from services.ollama import OllamaService
from services.vector_store import VectorStoreService


@pytest.fixture
def ollama_service():
    """Create OllamaService instance."""
    return OllamaService()


@pytest.fixture
def vector_store():
    """Create VectorStoreService instance."""
    return VectorStoreService()


@pytest.fixture
async def rag_indexer(ollama_service, vector_store):
    """Create RAG.Indexer agent."""
    return RAGIndexerAgent(
        ollama_service=ollama_service,
        vector_store=vector_store,
        chunk_size=128,  # Small for testing
        chunk_overlap=32,
    )


@pytest.fixture
async def rag_searcher(ollama_service, vector_store):
    """Create RAG.Searcher agent."""
    return RAGSearcherAgent(
        ollama_service=ollama_service,
        vector_store=vector_store,
        top_k=3,
        score_threshold=0.5,
    )


@pytest.fixture
def rag_citation():
    """Create RAG.Citation agent."""
    return RAGCitationAgent(max_snippet_length=200)


class TestRAGIndexer:
    """Tests for RAG.Indexer agent."""

    @pytest.mark.asyncio
    async def test_indexer_basic(self, rag_indexer):
        """Test basic document indexing."""
        request = AgentExecutionRequest(
            agent_id="rag.indexer",
            payload={
                "content": "This is a test document about AI and machine learning.",
                "doc_id": "test_doc_1",
                "metadata": {"author": "Test", "year": "2025"},
            },
        )

        result = await rag_indexer.execute(request)

        assert result.success is True
        assert result.output["chunks_created"] > 0
        assert "chunk_ids" in result.output
        assert result.output["doc_id"] == "test_doc_1"

    @pytest.mark.asyncio
    async def test_indexer_empty_content(self, rag_indexer):
        """Test indexing with empty content."""
        request = AgentExecutionRequest(
            agent_id="rag.indexer",
            payload={"content": "", "doc_id": "empty_doc"},
        )

        result = await rag_indexer.execute(request)

        assert result.success is False
        assert "No content provided" in result.error

    @pytest.mark.asyncio
    async def test_chunking(self, rag_indexer):
        """Test document chunking logic."""
        long_text = "A" * 300  # Text longer than chunk_size
        chunks = rag_indexer._chunk_document(
            content=long_text,
            doc_id="test_doc",
            metadata={},
        )

        assert len(chunks) > 1  # Should create multiple chunks
        assert all(chunk.doc_id == "test_doc" for chunk in chunks)
        assert all(chunk.chunk_id for chunk in chunks)  # All have IDs


class TestRAGSearcher:
    """Tests for RAG.Searcher agent."""

    @pytest.mark.asyncio
    async def test_searcher_basic(self, rag_searcher, rag_indexer):
        """Test basic search after indexing."""
        # First index a document
        index_request = AgentExecutionRequest(
            agent_id="rag.indexer",
            payload={
                "content": "Python is a programming language. It is widely used for AI.",
                "doc_id": "python_doc",
                "metadata": {"title": "Python Guide"},
            },
        )
        await rag_indexer.execute(index_request)

        # Then search
        search_request = AgentExecutionRequest(
            agent_id="rag.searcher",
            payload={"query": "programming language"},
        )

        result = await rag_searcher.execute(search_request)

        assert result.success is True
        assert "results" in result.output
        assert result.output["total_matches"] >= 0

    @pytest.mark.asyncio
    async def test_searcher_empty_query(self, rag_searcher):
        """Test search with empty query."""
        request = AgentExecutionRequest(
            agent_id="rag.searcher",
            payload={"query": ""},
        )

        result = await rag_searcher.execute(request)

        assert result.success is False
        assert "No query provided" in result.error


class TestRAGCitation:
    """Tests for RAG.Citation agent."""

    @pytest.mark.asyncio
    async def test_citation_markdown(self, rag_citation):
        """Test citation formatting in Markdown."""
        request = AgentExecutionRequest(
            agent_id="rag.citation",
            payload={
                "results": [
                    {
                        "doc_id": "doc1",
                        "content": "AI is transforming the world.",
                        "score": 0.95,
                        "metadata": {"title": "AI Report", "author": "Smith", "year": "2025"},
                    }
                ],
                "format": "markdown",
            },
        )

        result = await rag_citation.execute(request)

        assert result.success is True
        assert result.output["total_citations"] == 1
        assert "formatted_citations" in result.output
        assert "AI is transforming" in result.output["formatted_citations"][0]

    @pytest.mark.asyncio
    async def test_citation_apa(self, rag_citation):
        """Test citation formatting in APA."""
        request = AgentExecutionRequest(
            agent_id="rag.citation",
            payload={
                "results": [
                    {
                        "doc_id": "doc1",
                        "content": "Machine learning is a subset of AI.",
                        "score": 0.88,
                        "metadata": {"author": "Johnson", "year": "2024", "title": "ML Basics"},
                    }
                ],
                "format": "apa",
            },
        )

        result = await rag_citation.execute(request)

        assert result.success is True
        assert "Johnson (2024)" in result.output["formatted_citations"][0]

    @pytest.mark.asyncio
    async def test_citation_empty_results(self, rag_citation):
        """Test citation with no results."""
        request = AgentExecutionRequest(
            agent_id="rag.citation",
            payload={"results": [], "format": "markdown"},
        )

        result = await rag_citation.execute(request)

        assert result.success is False
        assert "No search results" in result.error
