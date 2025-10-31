"""
Service de gestion des utilisateurs avec PostgreSQL
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from config import get_settings
from models.db import Base, UserDB, APIKeyDB
from models.user import User, UserCreate, UserUpdate, UserRole, UserStatus, UserStats
from services.auth import AuthService

logger = logging.getLogger(__name__)


class UserService:
    """
    Service de gestion des utilisateurs avec PostgreSQL.
    """

    def __init__(self):
        self.auth_service = AuthService()
        settings = get_settings()

        # Create async engine (PostgreSQL ou SQLite)
        db_url = settings.database.postgres_url
        engine_kwargs = {"echo": False}

        # Pool settings only for PostgreSQL
        if "postgresql" in db_url:
            engine_kwargs.update({
                "pool_pre_ping": True,
                "pool_size": 5,
                "max_overflow": 10
            })

        self.engine = create_async_engine(db_url, **engine_kwargs)

        # Create async session factory
        self.SessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        db_type = "PostgreSQL" if "postgresql" in db_url else "SQLite"
        logger.info(f"[UserService] Service {db_type} initialisé")

    async def init_db(self):
        """Initialize database and create default admin if needed"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Create default admin if no users exist
        await self._create_default_admin()

    async def _create_default_admin(self):
        """Crée un compte admin par défaut si aucun n'existe"""
        async with self.SessionLocal() as session:
            # Check if any users exist
            result = await session.execute(select(UserDB).limit(1))
            if result.scalar_one_or_none() is not None:
                return  # Users already exist

            admin_id = str(uuid.uuid4())
            now = datetime.utcnow()

            admin = UserDB(
                id=admin_id,
                email="admin@agenticai.dev",
                username="admin",
                hashed_password=self.auth_service.hash_password("admin123"),
                full_name="Administrator",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                max_agents=1000,
                max_documents=10000,
                max_storage_mb=50000,
                default_model="qwen2.5:14b",
                language="fr",
                timezone="UTC"
            )

            session.add(admin)
            await session.commit()

            logger.info(f"[UserService] Admin par défaut créé: admin@agenticai.dev / admin123")

    async def create_user(self, user_create: UserCreate) -> User:
        """
        Crée un nouvel utilisateur.

        Args:
            user_create: Données de création

        Returns:
            Utilisateur créé

        Raises:
            ValueError: Si l'email existe déjà
        """
        async with self.SessionLocal() as session:
            user_id = str(uuid.uuid4())
            now = datetime.utcnow()

            hashed_password = self.auth_service.hash_password(user_create.password)

            user_db = UserDB(
                id=user_id,
                email=user_create.email,
                username=user_create.username,
                hashed_password=hashed_password,
                full_name=user_create.full_name,
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                max_agents=50,
                max_documents=1000,
                max_storage_mb=5000,
                default_model="qwen2.5:14b",
                language="fr",
                timezone="UTC"
            )

            session.add(user_db)

            try:
                await session.commit()
                await session.refresh(user_db)
            except IntegrityError as e:
                await session.rollback()
                if "email" in str(e):
                    raise ValueError(f"Email {user_create.email} déjà utilisé")
                elif "username" in str(e):
                    raise ValueError(f"Username {user_create.username} déjà utilisé")
                else:
                    raise ValueError(f"Erreur lors de la création de l'utilisateur: {e}")

            logger.info(f"[UserService] Utilisateur créé: {user_create.email} (id={user_id})")

            return self._user_db_to_model(user_db)

    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(UserDB).where(UserDB.id == user_id)
            )
            user_db = result.scalar_one_or_none()

            if not user_db:
                return None

            return self._user_db_to_model(user_db)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email.

        Args:
            email: Email de l'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(UserDB).where(UserDB.email == email)
            )
            user_db = result.scalar_one_or_none()

            if not user_db:
                return None

            return self._user_db_to_model(user_db)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur.

        Args:
            email: Email de l'utilisateur
            password: Mot de passe

        Returns:
            Utilisateur si authentification réussie, None sinon
        """
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(UserDB).where(UserDB.email == email)
            )
            user_db = result.scalar_one_or_none()

            if not user_db:
                logger.warning(f"[UserService] Utilisateur non trouvé: {email}")
                return None

            if user_db.status != UserStatus.ACTIVE:
                logger.warning(f"[UserService] Compte inactif: {email}")
                return None

            if not self.auth_service.verify_password(password, user_db.hashed_password):
                logger.warning(f"[UserService] Mot de passe incorrect: {email}")
                return None

            # Mettre à jour last_login
            user_db.last_login = datetime.utcnow()
            await session.commit()
            await session.refresh(user_db)

            logger.info(f"[UserService] Authentification réussie: {email}")

            return self._user_db_to_model(user_db)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """
        Met à jour un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            user_update: Données de mise à jour

        Returns:
            Utilisateur mis à jour ou None si non trouvé
        """
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(UserDB).where(UserDB.id == user_id)
            )
            user_db = result.scalar_one_or_none()

            if not user_db:
                return None

            # Mettre à jour les champs fournis
            update_data = user_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user_db, field, value)

            user_db.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(user_db)

            logger.info(f"[UserService] Utilisateur mis à jour: {user_id}")

            return self._user_db_to_model(user_db)

    async def delete_user(self, user_id: str) -> bool:
        """
        Supprime un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si supprimé, False si non trouvé
        """
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(UserDB).where(UserDB.id == user_id)
            )
            user_db = result.scalar_one_or_none()

            if not user_db:
                return False

            await session.delete(user_db)
            await session.commit()

            logger.info(f"[UserService] Utilisateur supprimé: {user_id}")

            return True

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None
    ) -> List[User]:
        """
        Liste les utilisateurs avec pagination.

        Args:
            skip: Nombre d'utilisateurs à sauter
            limit: Nombre maximum d'utilisateurs
            role: Filtrer par rôle (optionnel)

        Returns:
            Liste d'utilisateurs
        """
        async with self.SessionLocal() as session:
            query = select(UserDB)

            if role:
                query = query.where(UserDB.role == role)

            query = query.offset(skip).limit(limit)

            result = await session.execute(query)
            users_db = result.scalars().all()

            return [self._user_db_to_model(user_db) for user_db in users_db]

    async def create_api_key(self, user_id: str, name: Optional[str] = None) -> Optional[str]:
        """
        Génère une clé API pour un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            name: Nom de la clé API (optionnel)

        Returns:
            Clé API ou None si utilisateur non trouvé
        """
        async with self.SessionLocal() as session:
            # Vérifier que l'utilisateur existe
            result = await session.execute(
                select(UserDB).where(UserDB.id == user_id)
            )
            user_db = result.scalar_one_or_none()

            if not user_db:
                return None

            # Générer la clé API
            api_key = self.auth_service.generate_api_key(user_id)
            api_key_hash = self.auth_service.hash_api_key(api_key)

            # Créer l'entrée en base
            api_key_db = APIKeyDB(
                id=str(uuid.uuid4()),
                user_id=user_id,
                key_hash=api_key_hash,
                name=name,
                is_active=True,
                created_at=datetime.utcnow()
            )

            session.add(api_key_db)
            await session.commit()

            logger.info(f"[UserService] Clé API créée pour user_id={user_id}")

            return api_key

    async def verify_api_key(self, api_key: str) -> Optional[User]:
        """
        Vérifie une clé API et retourne l'utilisateur associé.

        Args:
            api_key: Clé API à vérifier

        Returns:
            Utilisateur si clé valide, None sinon
        """
        async with self.SessionLocal() as session:
            api_key_hash = self.auth_service.hash_api_key(api_key)

            result = await session.execute(
                select(APIKeyDB).where(
                    and_(
                        APIKeyDB.key_hash == api_key_hash,
                        APIKeyDB.is_active == True
                    )
                )
            )
            api_key_db = result.scalar_one_or_none()

            if not api_key_db:
                return None

            # Mettre à jour last_used_at
            api_key_db.last_used_at = datetime.utcnow()
            await session.commit()

            # Récupérer l'utilisateur
            return await self.get_user(api_key_db.user_id)

    async def get_user_stats(self, user_id: str) -> Optional[UserStats]:
        """
        Récupère les statistiques d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Statistiques ou None si utilisateur non trouvé
        """
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(UserDB).where(UserDB.id == user_id)
            )
            user_db = result.scalar_one_or_none()

            if not user_db:
                return None

            # TODO: Calculer les vraies statistiques depuis la DB
            # Pour l'instant, retourner des valeurs par défaut
            return UserStats(
                user_id=user_id,
                agents_count=0,
                documents_count=0,
                storage_used_mb=0.0,
                total_queries=0,
                last_activity=user_db.last_login
            )

    def _user_db_to_model(self, user_db: UserDB) -> User:
        """Convert UserDB to User model"""
        return User(
            id=user_db.id,
            email=user_db.email,
            username=user_db.username,
            full_name=user_db.full_name,
            role=user_db.role,
            status=user_db.status,
            created_at=user_db.created_at.isoformat() if user_db.created_at else None,
            updated_at=user_db.updated_at.isoformat() if user_db.updated_at else None,
            last_login=user_db.last_login.isoformat() if user_db.last_login else None,
            max_agents=user_db.max_agents,
            max_documents=user_db.max_documents,
            max_storage_mb=user_db.max_storage_mb,
            default_model=user_db.default_model,
            language=user_db.language,
            timezone=user_db.timezone
        )
