"""
Routes d'authentification
"""

import logging
from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.user import (
    User,
    UserCreate,
    UserLogin,
    UserUpdate,
    Token,
    TokenData,
    UserStats
)
from services.auth import AuthService
from services.user import UserService
from api.dependencies import get_current_user, get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

# Services
auth_service = AuthService()
user_service = UserService()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """
    Inscription d'un nouvel utilisateur.

    Crée un compte utilisateur avec les informations fournies.
    """
    try:
        user = await user_service.create_user(user_create)
        logger.info(f"[Auth] Nouvel utilisateur enregistré: {user.email}")
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[Auth] Erreur inscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'inscription"
        )


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """
    Connexion d'un utilisateur.

    Authentifie l'utilisateur et retourne un token JWT.
    """
    # Authentifier l'utilisateur
    user = await user_service.authenticate(user_login.email, user_login.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Créer le token
    access_token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role
    )

    logger.info(f"[Auth] Connexion réussie: {user.email}")

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Renouvelle un access token avec un refresh token.
    """
    user_id = auth_service.verify_refresh_token(refresh_token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide"
        )

    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    # Créer un nouveau token
    access_token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Récupère les informations de l'utilisateur connecté.
    """
    return current_user


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Met à jour les informations de l'utilisateur connecté.
    """
    updated_user = await user_service.update_user(current_user.id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    logger.info(f"[Auth] Profil mis à jour: {current_user.email}")

    return updated_user


@router.get("/me/stats", response_model=UserStats)
async def get_current_user_stats(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Récupère les statistiques de l'utilisateur connecté.
    """
    stats = await user_service.get_user_stats(current_user.id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statistiques non disponibles"
        )

    return stats


@router.post("/me/api-key", response_model=dict)
async def create_api_key(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Génère une nouvelle clé API pour l'utilisateur.

    ⚠️ La clé n'est affichée qu'une seule fois. Sauvegardez-la !
    """
    api_key = await user_service.create_api_key(current_user.id)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Impossible de générer la clé API"
        )

    logger.info(f"[Auth] Clé API créée pour: {current_user.email}")

    return {
        "api_key": api_key,
        "message": "Sauvegardez cette clé, elle ne sera plus affichée !"
    }


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Déconnexion de l'utilisateur.

    Note: Avec JWT, la déconnexion est gérée côté client en supprimant le token.
    Cette route existe pour la cohérence de l'API.
    """
    logger.info(f"[Auth] Déconnexion: {current_user.email}")

    return {"message": "Déconnexion réussie"}


@router.post("/test-token", response_model=TokenData)
async def test_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """
    Endpoint de test pour vérifier un token JWT.
    """
    token = credentials.credentials
    token_data = auth_service.verify_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

    return token_data
