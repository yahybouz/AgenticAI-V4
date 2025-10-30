"""
Modèles SQLAlchemy pour les utilisateurs
"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column

from models.db.base import Base
from models.user import UserRole, UserStatus


class UserDB(Base):
    """Table utilisateurs"""
    __tablename__ = "users"

    # Clé primaire
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Authentification
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profil
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Rôle et statut
    role: Mapped[str] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.USER
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(UserStatus),
        nullable=False,
        default=UserStatus.ACTIVE
    )

    # Quotas
    max_agents: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    max_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    max_storage_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=5000)

    # Préférences
    default_model: Mapped[str] = mapped_column(String(100), nullable=False, default="qwen2.5:14b")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="fr")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Index composites pour les recherches fréquentes
    __table_args__ = (
        Index('idx_user_status_role', 'status', 'role'),
        Index('idx_user_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class APIKeyDB(Base):
    """Table clés API"""
    __tablename__ = "api_keys"

    # Clé primaire
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Relation utilisateur
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Clé API hashée (stockage sécurisé)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # Nom/description de la clé
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Statut
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Index
    __table_args__ = (
        Index('idx_apikey_user_active', 'user_id', 'is_active'),
    )

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, user_id={self.user_id}, active={self.is_active})>"
