"""
Modèles utilisateur pour l'authentification et la gestion multi-tenant
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRole(str, Enum):
    """Rôles utilisateur"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserStatus(str, Enum):
    """Statut du compte utilisateur"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    """Modèle utilisateur complet"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    # Quotas et limites
    max_agents: int = 50
    max_documents: int = 1000
    max_storage_mb: int = 5000

    # Préférences
    default_model: str = "qwen2.5:14b"
    language: str = "fr"
    timezone: str = "UTC"


class UserCreate(BaseModel):
    """Modèle pour créer un utilisateur"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    """Modèle pour mettre à jour un utilisateur"""
    full_name: Optional[str] = None
    default_model: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


class UserLogin(BaseModel):
    """Modèle pour la connexion"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Modèle de token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Secondes


class TokenData(BaseModel):
    """Données contenues dans le token"""
    user_id: str
    email: str
    role: UserRole


class UserStats(BaseModel):
    """Statistiques utilisateur"""
    user_id: str
    agents_count: int = 0
    documents_count: int = 0
    storage_used_mb: float = 0.0
    total_queries: int = 0
    last_activity: Optional[datetime] = None
