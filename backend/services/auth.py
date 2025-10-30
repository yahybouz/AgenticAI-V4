"""
Service d'authentification avec JWT
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets

from jose import JWTError, jwt
import bcrypt

from models.user import User, UserCreate, TokenData, UserRole
from config import get_settings

logger = logging.getLogger(__name__)

# Configuration
settings = get_settings()


class AuthService:
    """Service d'authentification et gestion des tokens JWT"""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24 * 7  # 7 jours

    def hash_password(self, password: str) -> str:
        """
        Hash un mot de passe avec bcrypt.

        Args:
            password: Mot de passe en clair

        Returns:
            Hash du mot de passe
        """
        # Convertir en bytes et hasher
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie un mot de passe contre son hash.

        Args:
            plain_password: Mot de passe en clair
            hashed_password: Hash du mot de passe

        Returns:
            True si le mot de passe est correct
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crée un token JWT d'accès.

        Args:
            user_id: ID de l'utilisateur
            email: Email de l'utilisateur
            role: Rôle de l'utilisateur
            expires_delta: Durée de validité custom

        Returns:
            Token JWT encodé
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode = {
            "sub": user_id,
            "email": email,
            "role": role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.info(f"[AuthService] Token créé pour user_id={user_id}")

        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Vérifie et décode un token JWT.

        Args:
            token: Token JWT à vérifier

        Returns:
            Données du token si valide, None sinon
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")

            if user_id is None or email is None:
                logger.warning("[AuthService] Token invalide: données manquantes")
                return None

            token_data = TokenData(
                user_id=user_id,
                email=email,
                role=UserRole(role)
            )

            return token_data

        except JWTError as e:
            logger.warning(f"[AuthService] Erreur JWT: {e}")
            return None

    def generate_api_key(self, user_id: str) -> str:
        """
        Génère une clé API pour un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Clé API unique
        """
        # Générer un token aléatoire sécurisé
        random_part = secrets.token_urlsafe(32)

        # Ajouter un préfixe identifiable
        api_key = f"aai_v4_{random_part}"

        logger.info(f"[AuthService] Clé API générée pour user_id={user_id}")

        return api_key

    def hash_api_key(self, api_key: str) -> str:
        """
        Hash une clé API pour stockage sécurisé.

        Args:
            api_key: Clé API en clair

        Returns:
            Hash de la clé API
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    def create_refresh_token(self, user_id: str) -> str:
        """
        Crée un refresh token pour renouveler l'access token.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Refresh token JWT
        """
        expire = datetime.utcnow() + timedelta(days=30)  # 30 jours

        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.info(f"[AuthService] Refresh token créé pour user_id={user_id}")

        return encoded_jwt

    def verify_refresh_token(self, token: str) -> Optional[str]:
        """
        Vérifie un refresh token et retourne l'user_id.

        Args:
            token: Refresh token à vérifier

        Returns:
            user_id si valide, None sinon
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != "refresh":
                logger.warning("[AuthService] Token n'est pas un refresh token")
                return None

            user_id: str = payload.get("sub")
            return user_id

        except JWTError as e:
            logger.warning(f"[AuthService] Erreur refresh token: {e}")
            return None
