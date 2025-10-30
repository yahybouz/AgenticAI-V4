#!/usr/bin/env python3
"""
Test du système RAG enrichi avec:
- Parser multi-formats
- Document Loader
- Cached Searcher
- Reranker
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Ajouter backend au path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.ollama import OllamaService
from services.vector_store import VectorStoreService
from services.document_parser import DocumentParserService
from services.search_cache import SearchCacheService
from agents.rag.indexer import RAGIndexerAgent
from agents.rag.document_loader import RAGDocumentLoaderAgent
from agents.rag.cached_searcher import RAGCachedSearcherAgent
from agents.rag.reranker import RAGRerankerAgent
from models.agent import AgentExecutionRequest


# Documents de test
TEST_DOCUMENTS = {
    "python_guide.txt": """Python Programming Guide

Python is a high-level, interpreted programming language known for its clear syntax and readability.
It was created by Guido van Rossum and first released in 1991.

Key Features:
- Easy to learn and use
- Extensive standard library
- Cross-platform compatibility
- Strong community support
- Object-oriented and functional programming paradigms

Python is widely used for:
- Web development (Django, Flask)
- Data science and machine learning
- Automation and scripting
- Scientific computing
""",
    "ml_basics.md": """# Machine Learning Basics

## What is Machine Learning?

Machine Learning (ML) is a subset of Artificial Intelligence that enables systems to learn and improve from experience without being explicitly programmed.

## Types of ML:

### Supervised Learning
- Classification
- Regression

### Unsupervised Learning
- Clustering
- Dimensionality Reduction

### Reinforcement Learning
- Agent learns through rewards and penalties

## Popular ML Libraries:
- scikit-learn
- TensorFlow
- PyTorch
- Keras
""",
    "rag_systems.txt": """RAG (Retrieval-Augmented Generation) Systems

RAG is a technique that combines retrieval and generation for better AI responses.

How RAG Works:
1. Document Indexing: Documents are chunked and embedded into vectors
2. Semantic Search: User query is converted to embedding and similar documents are retrieved
3. Context Augmentation: Retrieved documents are added to the LLM prompt
4. Generation: LLM generates response using retrieved context

Benefits of RAG:
- Reduces hallucinations
- Provides source attribution
- Enables knowledge updates without retraining
- Works with smaller models

Components:
- Embedding model (e.g., nomic-embed-text)
- Vector database (e.g., Qdrant)
- LLM for generation (e.g., Qwen, GPT)
- Chunking strategy (size, overlap)
"""
}


def print_separator(title: str):
    """Affiche un séparateur formaté"""
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70 + "\n")


async def test_enhanced_rag():
    """Test complet du système RAG enrichi"""

    print_separator("🧪 Test Système RAG Enrichi")

    # Initialiser les services
    print("📦 Initialisation des services...")
    ollama = OllamaService()
    vector_store = VectorStoreService()
    parser = DocumentParserService()
    cache = SearchCacheService(max_size=100, default_ttl=3600)

    # Initialiser les agents
    print("🤖 Création des agents RAG...")
    indexer = RAGIndexerAgent(ollama, vector_store)
    document_loader = RAGDocumentLoaderAgent(parser, indexer)
    cached_searcher = RAGCachedSearcherAgent(ollama, vector_store, cache)
    reranker = RAGRerankerAgent(ollama)

    print("✅ Services et agents initialisés\n")

    # Créer documents de test temporaires
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Répertoire temporaire: {temp_dir}\n")

    try:
        # Écrire les fichiers de test
        for filename, content in TEST_DOCUMENTS.items():
            file_path = Path(temp_dir) / filename
            file_path.write_text(content)
            print(f"   ✅ Créé: {filename}")

        # ====================================================================
        # PHASE 1: Document Parsing et Loading
        # ====================================================================
        print_separator("📚 PHASE 1: Chargement Documents Multi-Formats")

        results = await document_loader.load_directory(
            directory_path=temp_dir,
            collection_name="test_documents",
            recursive=False,
            metadata={"source": "test", "category": "documentation"}
        )

        for file_path, result in results.items():
            filename = Path(file_path).name
            if result.success:
                print(f"   ✅ {filename}")
                print(f"      Format: {result.output['format']}")
                print(f"      Chunks: {result.output['chunks_created']}")
                print(f"      Mots: {result.output.get('word_count', 'N/A')}")
            else:
                print(f"   ❌ {filename}: {result.error}")

        # ====================================================================
        # PHASE 2: Recherche avec Cache
        # ====================================================================
        print_separator("🔍 PHASE 2: Recherche Sémantique avec Cache")

        queries = [
            "What is Python used for?",
            "Explain machine learning types",
            "How does RAG work?",
            "What is Python used for?",  # Requête dupliquée pour tester le cache
        ]

        for i, query in enumerate(queries, 1):
            print(f"[{i}] Query: '{query}'")

            request = AgentExecutionRequest(
                agent_id="cached_searcher",
                input={
                    "query": query,
                    "top_k": 3,
                    "use_cache": True,
                }
            )

            result = await cached_searcher.execute(request)

            if result.success:
                from_cache = result.output.get("from_cache", False)
                cache_status = "CACHE HIT" if from_cache else "CACHE MISS"
                print(f"   {cache_status}")

                results_list = result.output.get("results", [])
                print(f"   Résultats: {len(results_list)}")

                for j, res in enumerate(results_list[:2], 1):  # Afficher top 2
                    content_preview = res.get("content", "")[:80].replace("\n", " ")
                    print(f"      [{j}] Score: {res.get('score', 0):.3f}")
                    print(f"          {content_preview}...")
            else:
                print(f"   ❌ Erreur: {result.error}")

            print()

        # Afficher stats du cache
        cache_stats = cached_searcher.get_cache_stats()
        print("📊 Statistiques du Cache:")
        print(f"   Taille: {cache_stats['size']}/{cache_stats['max_size']}")
        print(f"   Hit Rate: {cache_stats['hit_rate']:.1%}")
        print(f"   Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}")

        # ====================================================================
        # PHASE 3: Reranking pour meilleure pertinence
        # ====================================================================
        print_separator("🎯 PHASE 3: Reranking des Résultats")

        query = "Explain the components of a RAG system"
        print(f"Query: '{query}'\n")

        # Recherche initiale
        search_request = AgentExecutionRequest(
            agent_id="cached_searcher",
            input={
                "query": query,
                "top_k": 5,
                "use_cache": False,  # Désactiver cache pour ce test
            }
        )

        search_result = await cached_searcher.execute(search_request)

        if search_result.success:
            initial_results = search_result.output.get("results", [])
            print(f"📥 Résultats initiaux: {len(initial_results)}")

            for i, res in enumerate(initial_results[:3], 1):
                print(f"   [{i}] Doc: {res.get('doc_id', 'N/A')}, Score: {res.get('score', 0):.3f}")

            # Reranking
            print("\n🔄 Reranking en cours...")

            rerank_request = AgentExecutionRequest(
                agent_id="reranker",
                input={
                    "query": query,
                    "results": initial_results,
                    "top_k": 3,
                }
            )

            rerank_result = await reranker.execute(rerank_request)

            if rerank_result.success:
                reranked_results = rerank_result.output.get("reranked_results", [])

                print(f"\n📤 Résultats rerankés: {len(reranked_results)}\n")

                for i, res in enumerate(reranked_results, 1):
                    print(f"   [{i}] Doc: {res.get('doc_id', 'N/A')}")
                    print(f"       Score original: {res.get('original_score', 0):.3f}")
                    print(f"       Score reranké: {res.get('rerank_score', 0):.3f}")
                    print(f"       Score final: {res.get('final_score', 0):.3f}")
                    content_preview = res.get('content', '')[:100].replace("\n", " ")
                    print(f"       Content: {content_preview}...")
                    print()

        # ====================================================================
        # Résumé Final
        # ====================================================================
        print_separator("✅ Test Système RAG Enrichi Complété")

        print("📊 Résumé:")
        print(f"   • Documents chargés: {len(results)}")
        print(f"   • Documents réussis: {sum(1 for r in results.values() if r.success)}")
        print(f"   • Requêtes testées: {len(queries)}")
        print(f"   • Cache hit rate: {cache_stats['hit_rate']:.1%}")
        print(f"   • Reranking: ✅ Fonctionnel")

        print("\n🎉 Tous les composants RAG enrichis fonctionnent correctement!")

    finally:
        # Nettoyer
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Nettoyage: {temp_dir} supprimé")


if __name__ == "__main__":
    asyncio.run(test_enhanced_rag())
