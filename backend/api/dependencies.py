from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from agents import AgentRegistry, get_registry
from orchestrators import MasterOrchestrator
from services import (
    AgentExecutor,
    DatabaseService,
    MessagingService,
    MonitoringService,
    OllamaService,
    VectorStoreService,
)
from models.user import User, UserStatus, TokenData
from services.auth import AuthService
from services.user import UserService

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


@lru_cache
def get_agent_registry() -> AgentRegistry:
    return get_registry()


@lru_cache
def get_ollama_service() -> OllamaService:
    return OllamaService()


@lru_cache
def get_vector_store() -> VectorStoreService:
    return VectorStoreService()


@lru_cache
def get_database_service() -> DatabaseService:
    return DatabaseService()


@lru_cache
def get_messaging_service() -> MessagingService:
    return MessagingService()


@lru_cache
def get_monitoring_service() -> MonitoringService:
    return MonitoringService()


@lru_cache
def get_agent_executor() -> AgentExecutor:
    return AgentExecutor(
        registry=get_agent_registry(),
        database=get_database_service(),
    )


@lru_cache
def get_master_orchestrator() -> MasterOrchestrator:
    return MasterOrchestrator(
        registry=get_agent_registry(),
        executor=get_agent_executor(),
        ollama=get_ollama_service(),
        vector_store=get_vector_store(),
        database=get_database_service(),
        messaging=get_messaging_service(),
    )


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService()


@lru_cache
def get_user_service() -> UserService:
    return UserService()


# Authentication dependencies
async def get_token_data(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenData:
    """
    Extrait et vérifie le token JWT depuis les headers.
    """
    token = credentials.credentials
    token_data = auth_service.verify_token(token)

    if not token_data:
        logger.warning("[Dependencies] Token invalide")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def get_current_user(
    token_data: Annotated[TokenData, Depends(get_token_data)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """
    Récupère l'utilisateur courant depuis le token.
    """
    user = await user_service.get_user(token_data.user_id)

    if not user:
        logger.warning(f"[Dependencies] Utilisateur non trouvé: {token_data.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Vérifie que l'utilisateur courant est actif.
    """
    if current_user.status != UserStatus.ACTIVE:
        logger.warning(f"[Dependencies] Compte inactif: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte inactif ou suspendu"
        )

    return current_user


async def verify_api_key(
    api_key: str,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """
    Vérifie une clé API et retourne l'utilisateur.
    """
    user = await user_service.verify_api_key(api_key)

    if not user:
        logger.warning("[Dependencies] Clé API invalide")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide"
        )

    if user.status != UserStatus.ACTIVE:
        logger.warning(f"[Dependencies] Compte inactif (API key): {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte inactif"
        )

    return user
