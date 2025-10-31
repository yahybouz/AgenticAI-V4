"""
Route API pour le chat avec l'orchestrateur multi-agents
"""
from __future__ import annotations

from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import uuid

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
    # orchestrator=Depends(get_master_orchestrator)  # Temporairement désactivé
):
    """
    Envoie un message à l'orchestrateur et retourne la réponse.

    L'orchestrateur choisit automatiquement le meilleur agent pour répondre.

    NOTE: Version de démonstration - L'orchestrateur complet sera activé
    une fois le problème de logging résolu.
    """
    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")

    # VERSION DEMO: Réponse intelligente basique
    # TODO: Réactiver l'orchestrateur une fois le bug de logging fixé

    user_message = message.content.lower()

    # Réponses intelligentes basées sur le contenu
    if any(word in user_message for word in ["bonjour", "salut", "hello", "hi"]):
        demo_response = f"Bonjour {current_user.username} ! Je suis AgenticAI, votre assistant multi-agents intelligent. Je suis actuellement en mode démonstration, mais je peux déjà vous aider ! Comment puis-je vous assister aujourd'hui ?"
        agent = "chat.greeter"

    elif any(word in user_message for word in ["qui es-tu", "qui es tu", "présente-toi", "what are you"]):
        demo_response = "Je suis AgenticAI V4, un système d'intelligence artificielle multi-agents. Je suis composé de 19 agents spécialisés dans différents domaines : chat, coaching, documentation, emails, gestion de projets, RAG, voix et intelligence web. Mon orchestrateur intelligent route vos requêtes vers les agents les plus appropriés !"
        agent = "chat.assistant"

    elif any(word in user_message for word in ["aide", "help", "comment"]):
        demo_response = "Je peux vous aider dans de nombreux domaines :\n\n• 💬 Conversations générales\n• 📊 Gestion de projets\n• 📧 Traitement d'emails\n• 📚 Recherche de documents (RAG)\n• 🎤 Traitement vocal\n• 🌐 Intelligence web\n• 📝 Génération de documentation\n\nQue souhaitez-vous faire ?"
        agent = "chat.helper"

    elif any(word in user_message for word in ["agent", "agents"]):
        demo_response = "Actuellement, 19 agents sont disponibles dans le système, répartis en 8 domaines :\n\n1. **Chat** - Conversations générales\n2. **Coach** - Coaching et bien-être\n3. **Docs** - Documentation\n4. **Mail** - Gestion emails\n5. **PM** - Project Management\n6. **RAG** - Recherche documentaire\n7. **Voice** - Traitement vocal\n8. **WebIntel** - Intelligence web\n\nVous pouvez consulter la liste complète dans l'onglet 'Agents' !"
        agent = "info.agents"

    elif any(word in user_message for word in ["merci", "thank"]):
        demo_response = "Avec plaisir ! N'hésitez pas si vous avez d'autres questions. Je suis là pour vous aider ! 😊"
        agent = "chat.polite"

    else:
        demo_response = f"J'ai bien reçu votre message : '{message.content[:100]}{'...' if len(message.content) > 100 else ''}'\n\nJe suis actuellement en mode démonstration. L'orchestrateur complet avec connexion aux 19 agents sera activé prochainement. Pour l'instant, je peux répondre aux questions sur le système AgenticAI !"
        agent = "chat.demo"

    # Retourner la réponse formatée
    return ChatResponse(
        message=demo_response,
        trace_id=str(uuid.uuid4()),
        agent_used=agent,
        timestamp=datetime.utcnow().isoformat(),
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
