"""
Agent RAG Reranker - Réordonne les résultats de recherche par pertinence
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from models.agent import AgentExecutionRequest, AgentExecutionResult
from services.ollama import OllamaService

logger = logging.getLogger(__name__)


@dataclass
class RerankResult:
    """Résultat de reranking avec score amélioré"""
    doc_id: str
    chunk_id: str
    content: str
    original_score: float
    rerank_score: float
    final_score: float
    metadata: Dict


class RAGRerankerAgent:
    """
    Agent qui réordonne les résultats de recherche sémantique
    en utilisant un LLM pour évaluer la pertinence contextuelle.
    """

    def __init__(
        self,
        ollama_service: OllamaService,
        model: str = "qwen2.5:14b",
        weight_original: float = 0.3,
        weight_rerank: float = 0.7,
    ):
        """
        Args:
            ollama_service: Service Ollama pour requêtes LLM
            model: Modèle à utiliser pour le reranking
            weight_original: Poids du score de recherche vectorielle (0-1)
            weight_rerank: Poids du score de reranking LLM (0-1)
        """
        self.ollama = ollama_service
        self.model = model
        self.weight_original = weight_original
        self.weight_rerank = weight_rerank
        self.name = "RAG Reranker"
        self.description = "Réordonne les résultats de recherche par pertinence contextuelle"

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        """
        Réordonne les résultats de recherche.

        Args:
            request.input doit contenir:
                - query: Question de l'utilisateur
                - results: Liste des résultats à reranker
                  Chaque résultat doit avoir: doc_id, chunk_id, content, score, metadata
                - top_k: Nombre de résultats à retourner (optionnel, défaut: tous)

        Returns:
            AgentExecutionResult avec:
                - output.reranked_results: Liste ordonnée par pertinence
                - output.original_count: Nombre de résultats en entrée
                - output.returned_count: Nombre de résultats retournés
        """
        try:
            query = request.input.get("query")
            results = request.input.get("results", [])
            top_k = request.input.get("top_k")

            if not query:
                raise ValueError("query requis")

            if not results:
                logger.warning("[RAGReranker] Aucun résultat à reranker")
                return AgentExecutionResult(
                    success=True,
                    output={
                        "reranked_results": [],
                        "original_count": 0,
                        "returned_count": 0,
                    }
                )

            logger.info(f"[RAGReranker] Reranking {len(results)} résultats pour: {query[:50]}...")

            # Reranker chaque résultat
            reranked = []
            for result in results:
                rerank_score = await self._compute_relevance_score(
                    query=query,
                    content=result.get("content", ""),
                    metadata=result.get("metadata", {})
                )

                original_score = result.get("score", 0.5)

                # Combiner les scores
                final_score = (
                    self.weight_original * original_score +
                    self.weight_rerank * rerank_score
                )

                reranked.append(RerankResult(
                    doc_id=result.get("doc_id", ""),
                    chunk_id=result.get("chunk_id", result.get("id", "")),
                    content=result.get("content", ""),
                    original_score=original_score,
                    rerank_score=rerank_score,
                    final_score=final_score,
                    metadata=result.get("metadata", {})
                ))

            # Trier par score final décroissant
            reranked.sort(key=lambda x: x.final_score, reverse=True)

            # Limiter à top_k si spécifié
            if top_k and top_k > 0:
                reranked = reranked[:top_k]

            # Convertir en dict pour sérialisation
            reranked_results = [
                {
                    "doc_id": r.doc_id,
                    "chunk_id": r.chunk_id,
                    "content": r.content,
                    "original_score": r.original_score,
                    "rerank_score": r.rerank_score,
                    "final_score": r.final_score,
                    "metadata": r.metadata,
                }
                for r in reranked
            ]

            logger.info(f"[RAGReranker] Reranking terminé - Top score: {reranked[0].final_score:.3f}")

            return AgentExecutionResult(
                success=True,
                output={
                    "reranked_results": reranked_results,
                    "original_count": len(results),
                    "returned_count": len(reranked_results),
                }
            )

        except ValueError as e:
            logger.error(f"[RAGReranker] Erreur validation: {e}")
            return AgentExecutionResult(
                success=False,
                output={},
                error=f"Erreur validation: {str(e)}"
            )
        except Exception as e:
            logger.error(f"[RAGReranker] Erreur: {e}", exc_info=True)
            return AgentExecutionResult(
                success=False,
                output={},
                error=f"Reranking échoué: {str(e)}"
            )

    async def _compute_relevance_score(
        self,
        query: str,
        content: str,
        metadata: Dict
    ) -> float:
        """
        Calcule un score de pertinence entre 0 et 1 en utilisant un LLM.

        Args:
            query: Question de l'utilisateur
            content: Contenu du document
            metadata: Métadonnées du document

        Returns:
            Score de pertinence entre 0.0 et 1.0
        """
        try:
            # Construire le prompt pour évaluation de pertinence
            prompt = self._build_relevance_prompt(query, content, metadata)

            # Requête au LLM
            response = await self.ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.1,  # Faible pour cohérence
                    "num_predict": 100,  # Court pour vitesse
                }
            )

            # Extraire et parser le score
            score = self._parse_relevance_score(response)

            logger.debug(f"[RAGReranker] Score calculé: {score:.3f}")

            return score

        except Exception as e:
            logger.error(f"[RAGReranker] Erreur calcul score: {e}")
            # Score neutre en cas d'erreur
            return 0.5

    def _build_relevance_prompt(self, query: str, content: str, metadata: Dict) -> str:
        """Construit le prompt pour évaluation de pertinence"""
        # Limiter le contenu pour performance
        content_preview = content[:800] + ("..." if len(content) > 800 else "")

        title = metadata.get("title", "Document sans titre")

        prompt = f"""Évalue la pertinence de ce document par rapport à la question.

Question: {query}

Document: {title}
Contenu: {content_preview}

Analyse si ce document peut répondre à la question. Donne un score de pertinence:
- 0.0 à 0.3: Pas pertinent ou hors sujet
- 0.4 à 0.6: Légèrement pertinent, information partielle
- 0.7 à 0.8: Pertinent, contient des informations utiles
- 0.9 à 1.0: Très pertinent, répond directement à la question

Réponds uniquement avec le score numérique (ex: 0.75)"""

        return prompt

    def _parse_relevance_score(self, response: str) -> float:
        """
        Parse le score de pertinence depuis la réponse du LLM.

        Recherche un nombre décimal entre 0 et 1.
        """
        import re

        # Nettoyer la réponse
        response = response.strip().lower()

        # Chercher un nombre décimal (ex: 0.75, 0.8, .5)
        match = re.search(r'(\d*\.\d+|\d+\.?\d*)', response)

        if match:
            try:
                score = float(match.group(1))
                # Normaliser entre 0 et 1
                if score > 1.0:
                    score = score / 10.0  # Ex: 7.5 -> 0.75
                if score > 1.0:
                    score = 1.0
                if score < 0.0:
                    score = 0.0
                return score
            except ValueError:
                pass

        # Fallback: rechercher des mots-clés de pertinence
        if any(word in response for word in ["très pertinent", "highly relevant", "excellent"]):
            return 0.9
        elif any(word in response for word in ["pertinent", "relevant", "utile"]):
            return 0.7
        elif any(word in response for word in ["peu pertinent", "partially", "somewhat"]):
            return 0.5
        elif any(word in response for word in ["pas pertinent", "not relevant", "hors sujet"]):
            return 0.2

        # Score neutre par défaut
        logger.warning(f"[RAGReranker] Impossible de parser score: {response[:100]}")
        return 0.5
