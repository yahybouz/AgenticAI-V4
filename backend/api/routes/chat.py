"""
Route API pour le chat avec l'orchestrateur multi-agents
"""
from __future__ import annotations

from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
import json

from api.dependencies import get_master_orchestrator, get_current_active_user, get_ollama_service
from services.ollama import OllamaService
from models import AgentDomain, OrchestrationRequest
from models.user import User

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    """Message de chat"""
    content: str
    context: dict = {}


class ChatResponse(BaseModel):
    """Réponse du chat"""
    message: str
    trace_id: str
    agent_used: str | None = None
    timestamp: str


@router.post("/send", response_model=ChatResponse)
async def send_message(
    current_user: Annotated[User, Depends(get_current_active_user)],
    message: ChatMessage,
    ollama: Annotated[OllamaService, Depends(get_ollama_service)]
):
    """
    Envoie un message et retourne une réponse générée par Ollama.

    Le système utilise le LLM local (qwen2.5:14b) pour générer des réponses
    intelligentes et contextualisées.
    """
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")

    # System prompt pour AgenticAI
    system_prompt = f"""Tu es AgenticAI, un assistant intelligent multi-agents.

Informations contextuelles:
- Utilisateur: {current_user.username} ({current_user.email})
- Rôle: {current_user.role}
- Système: AgenticAI V4 avec 19 agents spécialisés

Tu disposes de 19 agents répartis en 8 domaines:
1. Chat - Conversations générales
2. Coach - Coaching et bien-être
3. Docs - Génération de documentation
4. Mail - Traitement d'emails
5. PM - Gestion de projets
6. RAG - Recherche documentaire
7. Voice - Traitement vocal
8. WebIntel - Intelligence web

Réponds de manière professionnelle, concise et utile. Adapte ton ton selon le contexte.
Si on te demande des informations sur le système, explique ses capacités.
Tu peux converser en français et en anglais."""

    try:
        # Vérifier si Ollama est disponible
        is_available = await ollama.is_available()

        if not is_available:
            # Fallback en mode démo si Ollama n'est pas disponible
            demo_response = f"⚠️ Service Ollama temporairement indisponible.\n\nJe suis AgenticAI, votre assistant multi-agents. Le système LLM sera de retour sous peu. En attendant, je peux vous donner des informations sur le système AgenticAI V4 et ses 19 agents spécialisés."
            agent = "chat.fallback"
        else:
            # Générer la réponse avec Ollama
            response_text = await ollama.chat_completion(
                user_message=message.content,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            demo_response = response_text
            agent = "ollama.qwen2.5"

    except Exception as e:
        # Fallback en cas d'erreur
        demo_response = f"Une erreur est survenue lors de la génération de la réponse. Je suis AgenticAI, votre assistant multi-agents intelligent. Comment puis-je vous aider ?"
        agent = "chat.error"

    # Retourner la réponse formatée
    return ChatResponse(
        message=demo_response,
        trace_id=str(uuid.uuid4()),
        agent_used=agent,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.post("/stream")
async def stream_message(
    current_user: Annotated[User, Depends(get_current_active_user)],
    message: ChatMessage,
    ollama: Annotated[OllamaService, Depends(get_ollama_service)]
):
    """
    Envoie un message et retourne une réponse en streaming.

    Format SSE (Server-Sent Events) pour affichage progressif.
    """
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")

    # System prompt pour AgenticAI
    system_prompt = f"""Tu es AgenticAI, un assistant intelligent multi-agents.

Informations contextuelles:
- Utilisateur: {current_user.username} ({current_user.email})
- Rôle: {current_user.role}
- Système: AgenticAI V4 avec 19 agents spécialisés

Tu disposes de 19 agents répartis en 8 domaines:
1. Chat - Conversations générales
2. Coach - Coaching et bien-être
3. Docs - Génération de documentation
4. Mail - Traitement d'emails
5. PM - Gestion de projets
6. RAG - Recherche documentaire
7. Voice - Traitement vocal
8. WebIntel - Intelligence web

Réponds de manière professionnelle, concise et utile. Adapte ton ton selon le contexte.
Si on te demande des informations sur le système, explique ses capacités.
Tu peux converser en français et en anglais."""

    async def generate_stream():
        """Générateur pour le streaming SSE"""
        try:
            # Vérifier si Ollama est disponible
            is_available = await ollama.is_available()

            if not is_available:
                # Fallback message
                yield f"data: {json.dumps({'content': '⚠️ Service Ollama temporairement indisponible.', 'done': False})}\n\n"
                yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
                return

            # Streamer depuis Ollama
            full_response = ""
            async for chunk in ollama.generate_stream(
                prompt=message.content,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            ):
                full_response += chunk
                # Envoyer le chunk au format SSE
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            # Signal de fin
            yield f"data: {json.dumps({'content': '', 'done': True, 'agent': 'ollama.qwen2.5'})}\n\n"

        except Exception as e:
            # En cas d'erreur, envoyer un message d'erreur
            error_msg = "Une erreur est survenue. Je suis AgenticAI, votre assistant multi-agents."
            yield f"data: {json.dumps({'content': error_msg, 'done': False})}\n\n"
            yield f"data: {json.dumps({'content': '', 'done': True, 'agent': 'chat.error'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Version avec orchestrateur (à réactiver plus tard)
"""
@router.post("/send-orchestrator", response_model=ChatResponse)
async def send_message_orchestrator(
    current_user: Annotated[User, Depends(get_current_active_user)],
    message: ChatMessage,
    orchestrator=Depends(get_master_orchestrator)
):
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")

    request = OrchestrationRequest(
        domain=AgentDomain.CHAT,
        objective="chat.respond",
        payload={
            "prompt": message.content,
            "user_id": str(current_user.id),
            "context": message.context,
        },
    )

    try:
        response = await orchestrator.execute(request)
        result_message = "Je suis désolé, je n'ai pas pu traiter votre demande."
        agent_used = None

        if response.result:
            if isinstance(response.result, dict):
                result_message = response.result.get("response", result_message)
                agent_used = response.result.get("agent", None)
            elif isinstance(response.result, str):
                result_message = response.result

        return ChatResponse(
            message=result_message,
            trace_id=response.trace.trace_id,
            agent_used=agent_used,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du message: {str(e)}"
        )
"""


@router.get("/history")
async def get_chat_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Récupère l'historique des conversations de l'utilisateur.

    Note: Pour l'instant, retourne un historique vide.
    À implémenter avec une vraie base de données.
    """
    # TODO: Implémenter la récupération depuis la BDD
    return {
        "messages": [],
        "user_id": str(current_user.id),
    }


@router.delete("/history")
async def clear_chat_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Efface l'historique des conversations de l'utilisateur.
    """
    # TODO: Implémenter la suppression depuis la BDD
    return {
        "status": "cleared",
        "user_id": str(current_user.id),
    }
