"""
Service de gestion des utilisateurs
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict

from models.user import User, UserCreate, UserUpdate, UserRole, UserStatus, UserStats
from services.auth import AuthService

logger = logging.getLogger(__name__)


class UserService:
    """
    Service de gestion des utilisateurs.

    Note: Cette implémentation utilise un stockage en mémoire.
    En production, remplacer par PostgreSQL.
    """

    def __init__(self):
        self.auth_service = AuthService()

        # Stockage en mémoire (remplacer par DB en production)
        self._users: Dict[str, Dict] = {}
        self._users_by_email: Dict[str, str] = {}  # email -> user_id
        self._passwords: Dict[str, str] = {}  # user_id -> hashed_password
        self._api_keys: Dict[str, str] = {}  # hashed_api_key -> user_id

        # Créer un utilisateur admin par défaut
        self._create_default_admin()

    def _create_default_admin(self):
        """Crée un compte admin par défaut si aucun n'existe"""
        if not self._users:
            admin_id = str(uuid.uuid4())
            now = datetime.utcnow()

            admin_data = {
                "id": admin_id,
                "email": "admin@agenticai.dev",
                "username": "admin",
                "full_name": "Administrator",
                "role": UserRole.ADMIN.value,
                "status": UserStatus.ACTIVE.value,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "last_login": None,
                "max_agents": 1000,
                "max_documents": 10000,
                "max_storage_mb": 50000,
                "default_model": "qwen2.5:14b",
                "language": "fr",
                "timezone": "UTC"
            }

            self._users[admin_id] = admin_data
            self._users_by_email["admin@agenticai.dev"] = admin_id
            self._passwords[admin_id] = self.auth_service.hash_password("admin123")

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
        # Vérifier si l'email existe déjà
        if user_create.email in self._users_by_email:
            raise ValueError(f"Email {user_create.email} déjà utilisé")

        # Générer un ID unique
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Hasher le mot de passe
        hashed_password = self.auth_service.hash_password(user_create.password)

        # Créer l'utilisateur
        user_data = {
            "id": user_id,
            "email": user_create.email,
            "username": user_create.username,
            "full_name": user_create.full_name,
            "role": UserRole.USER.value,
            "status": UserStatus.ACTIVE.value,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "last_login": None,
            "max_agents": 50,
            "max_documents": 1000,
            "max_storage_mb": 5000,
            "default_model": "qwen2.5:14b",
            "language": "fr",
            "timezone": "UTC"
        }

        self._users[user_id] = user_data
        self._users_by_email[user_create.email] = user_id
        self._passwords[user_id] = hashed_password

        logger.info(f"[UserService] Utilisateur créé: {user_create.email} (id={user_id})")

        return User(**user_data)

    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        user_data = self._users.get(user_id)
        if not user_data:
            return None

        return User(**user_data)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email.

        Args:
            email: Email de l'utilisateur

        Returns:
            Utilisateur ou None si non trouvé
        """
        user_id = self._users_by_email.get(email)
        if not user_id:
            return None

        return await self.get_user(user_id)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur.

        Args:
            email: Email de l'utilisateur
            password: Mot de passe

        Returns:
            Utilisateur si authentification réussie, None sinon
        """
        user = await self.get_user_by_email(email)
        if not user:
            logger.warning(f"[UserService] Utilisateur non trouvé: {email}")
            return None

        if user.status != UserStatus.ACTIVE:
            logger.warning(f"[UserService] Compte inactif: {email}")
            return None

        hashed_password = self._passwords.get(user.id)
        if not hashed_password:
            return None

        if not self.auth_service.verify_password(password, hashed_password):
            logger.warning(f"[UserService] Mot de passe incorrect: {email}")
            return None

        # Mettre à jour last_login
        user_data = self._users[user.id]
        user_data["last_login"] = datetime.utcnow().isoformat()

        logger.info(f"[UserService] Authentification réussie: {email}")

        return User(**user_data)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """
        Met à jour un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            user_update: Données de mise à jour

        Returns:
            Utilisateur mis à jour ou None si non trouvé
        """
        user_data = self._users.get(user_id)
        if not user_data:
            return None

        # Mettre à jour les champs fournis
        update_data = user_update.model_dump(exclude_unset=True)
        user_data.update(update_data)
        user_data["updated_at"] = datetime.utcnow().isoformat()

        logger.info(f"[UserService] Utilisateur mis à jour: {user_id}")

        return User(**user_data)

    async def delete_user(self, user_id: str) -> bool:
        """
        Supprime un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            True si supprimé, False si non trouvé
        """
        user_data = self._users.get(user_id)
        if not user_data:
            return False

        email = user_data["email"]

        # Supprimer de tous les dictionnaires
        del self._users[user_id]
        del self._users_by_email[email]
        if user_id in self._passwords:
            del self._passwords[user_id]

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
        users = []

        for user_data in self._users.values():
            if role and user_data["role"] != role.value:
                continue
            users.append(User(**user_data))

        # Pagination
        return users[skip:skip + limit]

    async def create_api_key(self, user_id: str) -> Optional[str]:
        """
        Génère une clé API pour un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Clé API ou None si utilisateur non trouvé
        """
        if user_id not in self._users:
            return None

        api_key = self.auth_service.generate_api_key(user_id)
        api_key_hash = self.auth_service.hash_api_key(api_key)

        self._api_keys[api_key_hash] = user_id

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
        api_key_hash = self.auth_service.hash_api_key(api_key)
        user_id = self._api_keys.get(api_key_hash)

        if not user_id:
            return None

        return await self.get_user(user_id)

    async def get_user_stats(self, user_id: str) -> Optional[UserStats]:
        """
        Récupère les statistiques d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Statistiques ou None si utilisateur non trouvé
        """
        if user_id not in self._users:
            return None

        # TODO: Calculer les vraies statistiques depuis la DB
        return UserStats(
            user_id=user_id,
            agents_count=0,
            documents_count=0,
            storage_used_mb=0.0,
            total_queries=0,
            last_activity=None
        )
