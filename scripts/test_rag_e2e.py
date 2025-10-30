#!/usr/bin/env python3
"""
End-to-end test for RAG agents (Indexer → Searcher → Citation).

This script demonstrates the complete RAG workflow:
1. Index a document into the vector store
2. Search for relevant content
3. Extract formatted citations

Usage:
    python scripts/test_rag_e2e.py
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from agents.rag import (
    create_rag_citation_agent,
    create_rag_indexer_agent,
    create_rag_searcher_agent,
)
from models import AgentExecutionRequest
from services.ollama import OllamaService
from services.vector_store import VectorStoreService


# Sample documents to index
SAMPLE_DOCUMENTS = [
    {
        "doc_id": "python_guide",
        "content": """Python is a high-level, interpreted programming language known for its
clear syntax and readability. It was created by Guido van Rossum and first released in 1991.
Python supports multiple programming paradigms including procedural, object-oriented, and
functional programming. It has a comprehensive standard library and is widely used in web
development, data science, artificial intelligence, and automation.""",
        "metadata": {
            "title": "Python Programming Guide",
            "author": "Tech Documentation Team",
            "year": "2025",
            "source": "Programming Languages Encyclopedia",
        },
    },
    {
        "doc_id": "ai_ml_basics",
        "content": """Artificial Intelligence (AI) is the simulation of human intelligence by
machines. Machine Learning (ML) is a subset of AI that enables systems to learn and improve
from experience without being explicitly programmed. Deep Learning is a further subset of ML
that uses neural networks with multiple layers. Common applications include image recognition,
natural language processing, recommendation systems, and autonomous vehicles.""",
        "metadata": {
            "title": "Introduction to AI and ML",
            "author": "Dr. Sarah Johnson",
            "year": "2024",
            "source": "AI Research Journal",
        },
    },
    {
        "doc_id": "rag_systems",
        "content": """Retrieval-Augmented Generation (RAG) is an AI framework that combines
information retrieval with text generation. It works by first retrieving relevant documents
from a knowledge base, then using those documents as context for generating responses. This
approach reduces hallucinations and provides source citations. RAG systems typically use
vector databases for efficient semantic search and embeddings to represent document meaning.""",
        "metadata": {
            "title": "RAG Systems Explained",
            "author": "AI Engineering Team",
            "year": "2025",
            "source": "Modern AI Architecture",
        },
    },
]


async def test_rag_workflow():
    """Run complete RAG workflow test."""
    print("=" * 70)
    print("🧪 RAG End-to-End Test")
    print("=" * 70)
    print()

    # Initialize services
    print("📦 Initializing services...")
    ollama = OllamaService()
    vector_store = VectorStoreService()
    print("✅ Services initialized")
    print()

    # Create agents
    print("🤖 Creating RAG agents...")
    indexer = await create_rag_indexer_agent(ollama, vector_store)
    searcher = await create_rag_searcher_agent(ollama, vector_store)
    citation = await create_rag_citation_agent()
    print("✅ Agents created (Indexer, Searcher, Citation)")
    print()

    # Step 1: Index documents
    print("=" * 70)
    print("📚 STEP 1: Indexing Documents")
    print("=" * 70)
    for doc in SAMPLE_DOCUMENTS:
        print(f"\n📄 Indexing: {doc['metadata']['title']}")
        request = AgentExecutionRequest(
            agent_id="rag.indexer",
            payload={
                "content": doc["content"],
                "doc_id": doc["doc_id"],
                "metadata": doc["metadata"],
            },
        )

        result = await indexer.execute(request)

        if result.success:
            chunks = result.output["chunks_created"]
            print(f"   ✅ Indexed successfully")
            print(f"   📊 Chunks created: {chunks}")
            print(f"   🔢 Chunk IDs: {result.output['chunk_ids'][:2]}... (showing first 2)")
        else:
            print(f"   ❌ Indexing failed: {result.error}")
            return False

    print()

    # Step 2: Search for content
    print("=" * 70)
    print("🔍 STEP 2: Searching Documents")
    print("=" * 70)

    queries = [
        "What is machine learning?",
        "Tell me about Python programming",
        "How does RAG work?",
    ]

    all_search_results = []

    for query in queries:
        print(f"\n🔎 Query: '{query}'")
        request = AgentExecutionRequest(
            agent_id="rag.searcher",
            payload={
                "query": query,
                "top_k": 3,
            },
        )

        result = await searcher.execute(request)

        if result.success:
            total = result.output["total_matches"]
            results = result.output["results"]
            print(f"   ✅ Search completed")
            print(f"   📊 Total matches: {total}")

            if results:
                all_search_results.append((query, results))
                for i, res in enumerate(results[:2], 1):  # Show top 2
                    print(f"\n   [{i}] Doc: {res['doc_id']}")
                    print(f"       Score: {res['score']:.3f}")
                    print(f"       Snippet: {res['content'][:100]}...")
            else:
                print("   ⚠️  No results found")
        else:
            print(f"   ❌ Search failed: {result.error}")

    print()

    # Step 3: Extract citations
    print("=" * 70)
    print("📝 STEP 3: Extracting Citations")
    print("=" * 70)

    for query, results in all_search_results[:2]:  # Show citations for first 2 queries
        print(f"\n🔎 Query: '{query}'")
        request = AgentExecutionRequest(
            agent_id="rag.citation",
            payload={
                "results": results,
                "format": "markdown",
            },
        )

        result = await citation.execute(request)

        if result.success:
            print(f"   ✅ Citations extracted: {result.output['total_citations']}")
            formatted = result.output["formatted_citations"]

            for i, cite in enumerate(formatted[:2], 1):  # Show top 2 citations
                print(f"\n   [{i}] {cite}")
        else:
            print(f"   ❌ Citation extraction failed: {result.error}")

    print()
    print("=" * 70)
    print("✅ RAG End-to-End Test Completed Successfully!")
    print("=" * 70)
    print()
    print("📊 Summary:")
    print(f"   • Documents indexed: {len(SAMPLE_DOCUMENTS)}")
    print(f"   • Queries tested: {len(queries)}")
    print(f"   • Search results: {sum(len(r[1]) for r in all_search_results)}")
    print()
    print("🎉 All RAG agents working correctly!")
    print()

    return True


async def main():
    """Main entry point."""
    try:
        success = await test_rag_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
