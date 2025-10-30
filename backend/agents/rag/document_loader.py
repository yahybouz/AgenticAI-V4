"""
Agent RAG Document Loader - Charge et indexe des documents de différents formats
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path

from models.agent import AgentExecutionRequest, AgentExecutionResult
from services.document_parser import DocumentParserService, DocumentFormat
from agents.rag.indexer import RAGIndexerAgent

logger = logging.getLogger(__name__)


class RAGDocumentLoaderAgent:
    """
    Agent spécialisé pour charger et indexer des documents multi-formats.
    Combine le parsing et l'indexation en une seule opération.
    """

    def __init__(
        self,
        parser: DocumentParserService,
        indexer: RAGIndexerAgent,
    ):
        self.parser = parser
        self.indexer = indexer
        self.name = "RAG Document Loader"
        self.description = "Charge et indexe des documents de multiples formats (PDF, DOCX, TXT, MD, HTML)"

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        """
        Charge un document et l'indexe dans le système RAG.

        Args:
            request.input doit contenir:
                - file_path: Chemin vers le fichier à charger
                - doc_id: ID unique du document (optionnel, déduit du fichier)
                - metadata: Métadonnées supplémentaires (optionnel)
                - collection_name: Nom de la collection (défaut: "documents")

        Returns:
            AgentExecutionResult avec:
                - output.chunks_created: Nombre de chunks créés
                - output.chunk_ids: Liste des IDs de chunks
                - output.format: Format du document détecté
                - output.metadata: Métadonnées extraites
        """
        try:
            file_path = request.input.get("file_path")
            if not file_path:
                raise ValueError("file_path requis")

            # Vérifier que le fichier existe
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Fichier introuvable: {file_path}")

            # Générer doc_id depuis le nom de fichier si non fourni
            doc_id = request.input.get("doc_id")
            if not doc_id:
                doc_id = Path(file_path).stem

            metadata = request.input.get("metadata", {})
            collection_name = request.input.get("collection_name", "documents")

            logger.info(f"[RAGDocumentLoader] Chargement: {file_path}")

            # 1. Parser le document
            parsed_doc = await self.parser.parse_file(file_path, metadata)

            logger.info(
                f"[RAGDocumentLoader] Document parsé - Format: {parsed_doc.format}, "
                f"Mots: {parsed_doc.word_count}, Pages: {parsed_doc.page_count or 'N/A'}"
            )

            # 2. Ajouter info de format dans les métadonnées
            final_metadata = {
                **parsed_doc.metadata,
                "format": parsed_doc.format.value,
                "word_count": str(parsed_doc.word_count or 0),
                "file_path": file_path,
            }

            if parsed_doc.page_count:
                final_metadata["page_count"] = str(parsed_doc.page_count)

            # 3. Indexer le document
            indexer_request = AgentExecutionRequest(
                agent_id="rag_indexer",
                input={
                    "doc_id": doc_id,
                    "content": parsed_doc.content,
                    "metadata": final_metadata,
                    "collection_name": collection_name,
                }
            )

            indexer_result = await self.indexer.execute(indexer_request)

            if not indexer_result.success:
                raise Exception(f"Indexation échouée: {indexer_result.error}")

            return AgentExecutionResult(
                success=True,
                output={
                    "doc_id": doc_id,
                    "chunks_created": indexer_result.output["chunks_created"],
                    "chunk_ids": indexer_result.output["chunk_ids"],
                    "format": parsed_doc.format.value,
                    "metadata": final_metadata,
                    "word_count": parsed_doc.word_count,
                    "page_count": parsed_doc.page_count,
                }
            )

        except FileNotFoundError as e:
            logger.error(f"[RAGDocumentLoader] Fichier introuvable: {e}")
            return AgentExecutionResult(
                success=False,
                output={},
                error=f"Fichier introuvable: {str(e)}"
            )
        except ValueError as e:
            logger.error(f"[RAGDocumentLoader] Erreur validation: {e}")
            return AgentExecutionResult(
                success=False,
                output={},
                error=f"Erreur validation: {str(e)}"
            )
        except Exception as e:
            logger.error(f"[RAGDocumentLoader] Erreur: {e}", exc_info=True)
            return AgentExecutionResult(
                success=False,
                output={},
                error=f"Chargement échoué: {str(e)}"
            )

    async def load_directory(
        self,
        directory_path: str,
        collection_name: str = "documents",
        recursive: bool = True,
        metadata: Optional[Dict] = None
    ) -> Dict[str, AgentExecutionResult]:
        """
        Charge tous les documents supportés d'un répertoire.

        Args:
            directory_path: Chemin du répertoire
            collection_name: Collection de destination
            recursive: Parcourir les sous-répertoires
            metadata: Métadonnées à ajouter à tous les documents

        Returns:
            Dict mapping file_path -> AgentExecutionResult
        """
        results = {}
        directory = Path(directory_path)

        if not directory.exists():
            logger.error(f"Répertoire introuvable: {directory_path}")
            return results

        # Obtenir les extensions supportées
        supported_extensions = self.parser.get_supported_extensions()

        # Pattern de recherche
        pattern = "**/*" if recursive else "*"

        logger.info(f"[RAGDocumentLoader] Scan: {directory_path} (recursive={recursive})")

        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in supported_extensions:
                continue

            logger.info(f"[RAGDocumentLoader] Traitement: {file_path}")

            request = AgentExecutionRequest(
                agent_id="rag_document_loader",
                input={
                    "file_path": str(file_path),
                    "metadata": metadata or {},
                    "collection_name": collection_name,
                }
            )

            result = await self.execute(request)
            results[str(file_path)] = result

        logger.info(
            f"[RAGDocumentLoader] Scan terminé - "
            f"Fichiers traités: {len(results)}, "
            f"Succès: {sum(1 for r in results.values() if r.success)}"
        )

        return results

    def get_supported_formats(self) -> List[str]:
        """Retourne la liste des formats supportés"""
        return [fmt.value for fmt in DocumentFormat if fmt != DocumentFormat.UNKNOWN]
