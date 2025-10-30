"""RAG.Citation Agent - Extract and format source citations."""
from __future__ import annotations

from typing import Any, Dict, List

from models import AgentExecutionRequest, AgentExecutionResult


class Citation:
    """Represents a source citation with formatting."""

    def __init__(
        self,
        doc_id: str,
        content_snippet: str,
        score: float,
        metadata: Dict[str, Any],
    ):
        self.doc_id = doc_id
        self.content_snippet = content_snippet
        self.score = score
        self.metadata = metadata

    def format_apa(self) -> str:
        """Format citation in APA style."""
        author = self.metadata.get("author", "Unknown")
        year = self.metadata.get("year", "n.d.")
        title = self.metadata.get("title", self.doc_id)
        source = self.metadata.get("source", "")

        if source:
            return f"{author} ({year}). {title}. {source}"
        return f"{author} ({year}). {title}"

    def format_markdown(self) -> str:
        """Format citation in Markdown with snippet."""
        title = self.metadata.get("title", self.doc_id)
        source = self.metadata.get("source", "")

        snippet = self._truncate_snippet(self.content_snippet, max_length=200)

        if source:
            return f"> {snippet}\n\n— *{title}*, {source} (relevance: {self.score:.2f})"
        return f"> {snippet}\n\n— *{title}* (relevance: {self.score:.2f})"

    def _truncate_snippet(self, text: str, max_length: int = 200) -> str:
        """Truncate snippet to max length, preserving words."""
        if len(text) <= max_length:
            return text

        truncated = text[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + "..."

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "doc_id": self.doc_id,
            "content_snippet": self.content_snippet,
            "score": self.score,
            "metadata": self.metadata,
            "formatted": {
                "apa": self.format_apa(),
                "markdown": self.format_markdown(),
            },
        }


class RAGCitationAgent:
    """
    Agent responsible for extracting and formatting source citations.

    Capabilities:
    - Extract relevant snippets from search results
    - Format citations in multiple styles (APA, Markdown, etc.)
    - Generate bibliographies
    - Track provenance
    """

    def __init__(self, max_snippet_length: int = 300):
        self.max_snippet_length = max_snippet_length

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        """
        Extract and format citations from search results.

        Input payload:
        - results: list[dict] - Search results from RAG.Searcher
        - format: str (optional) - Citation format ("apa", "markdown", "both")

        Returns:
        - citations: list[Citation]
        - format: str
        - total_citations: int
        """
        results = request.payload.get("results", [])
        citation_format = request.payload.get("format", "markdown")

        if not results:
            return AgentExecutionResult(
                success=False,
                output={},
                error="No search results provided for citation extraction",
            )

        try:
            # Create Citation objects from search results
            citations = []
            for result in results:
                citation = Citation(
                    doc_id=result["doc_id"],
                    content_snippet=result["content"],
                    score=result["score"],
                    metadata=result.get("metadata", {}),
                )
                citations.append(citation)

            # Format citations based on requested format
            if citation_format == "apa":
                formatted_citations = [c.format_apa() for c in citations]
            elif citation_format == "markdown":
                formatted_citations = [c.format_markdown() for c in citations]
            else:  # both
                formatted_citations = [c.to_dict()["formatted"] for c in citations]

            return AgentExecutionResult(
                success=True,
                output={
                    "citations": [c.to_dict() for c in citations],
                    "formatted_citations": formatted_citations,
                    "format": citation_format,
                    "total_citations": len(citations),
                },
                error=None,
            )

        except Exception as e:
            return AgentExecutionResult(
                success=False,
                output={},
                error=f"Citation extraction failed: {str(e)}",
            )


async def create_rag_citation_agent() -> RAGCitationAgent:
    """Factory function to create RAG.Citation agent."""
    return RAGCitationAgent(max_snippet_length=300)
