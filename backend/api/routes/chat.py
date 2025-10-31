"""
Route API pour le chat avec l'orchestrateur multi-agents
"""
from __future__ import annotations

from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencies import get_master_orchestrator, get_current_active_user
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
    orchestrator=Depends(get_master_orchestrator)
):
    """
    Envoie un message à l'orchestrateur et retourne la réponse.

    L'orchestrateur choisit automatiquement le meilleur agent pour répondre.
    """
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")

    # Créer la requête d'orchestration
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
        # Exécuter l'orchestration
        response = await orchestrator.execute(request)

        # Extraire la réponse
        result_message = "Je suis désolé, je n'ai pas pu traiter votre demande."
        agent_used = None

        if response.result:
            # Si on a un résultat, l'extraire
            if isinstance(response.result, dict):
                result_message = response.result.get("response", result_message)
                agent_used = response.result.get("agent", None)
            elif isinstance(response.result, str):
                result_message = response.result

        # Retourner la réponse formatée
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
