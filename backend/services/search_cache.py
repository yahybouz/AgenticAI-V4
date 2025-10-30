"""
Service de cache pour les résultats de recherche RAG.
Implémente un cache LRU (Least Recently Used) en mémoire.
"""

import logging
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import OrderedDict

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrée de cache avec métadonnées"""
    key: str
    value: Any
    created_at: float
    accessed_at: float
    access_count: int = 0
    ttl: Optional[float] = None  # Time-to-live en secondes


class SearchCacheService:
    """
    Service de cache LRU pour résultats de recherche.

    Features:
    - Cache LRU (Least Recently Used)
    - TTL (Time To Live) configurable par entrée
    - Statistiques d'utilisation
    - Nettoyage automatique des entrées expirées
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: Optional[float] = 3600.0,  # 1 heure par défaut
    ):
        """
        Args:
            max_size: Nombre maximum d'entrées dans le cache
            default_ttl: Durée de vie par défaut en secondes (None = infini)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # Statistiques
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
        }

    def _generate_key(self, query: str, **kwargs) -> str:
        """
        Génère une clé de cache unique basée sur la requête et les paramètres.

        Args:
            query: Requête de recherche
            **kwargs: Paramètres supplémentaires (collection, top_k, etc.)

        Returns:
            Clé de cache (hash SHA256)
        """
        # Combiner query et paramètres dans un string déterministe
        key_parts = [query]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        key_string = "|".join(key_parts)

        # Hash pour clé courte et unique
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    def get(
        self,
        query: str,
        **kwargs
    ) -> Optional[Any]:
        """
        Récupère une valeur du cache.

        Args:
            query: Requête de recherche
            **kwargs: Paramètres de recherche

        Returns:
            Valeur mise en cache ou None si absente/expirée
        """
        key = self._generate_key(query, **kwargs)

        if key not in self._cache:
            self.stats["misses"] += 1
            logger.debug(f"[SearchCache] MISS: {query[:50]}...")
            return None

        entry = self._cache[key]

        # Vérifier expiration
        if self._is_expired(entry):
            logger.debug(f"[SearchCache] EXPIRED: {query[:50]}...")
            self._remove(key)
            self.stats["expirations"] += 1
            self.stats["misses"] += 1
            return None

        # Mettre à jour statistiques d'accès
        entry.accessed_at = time.time()
        entry.access_count += 1

        # Déplacer en fin (most recently used)
        self._cache.move_to_end(key)

        self.stats["hits"] += 1
        logger.debug(f"[SearchCache] HIT: {query[:50]}... (accesses: {entry.access_count})")

        return entry.value

    def set(
        self,
        query: str,
        value: Any,
        ttl: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Stocke une valeur dans le cache.

        Args:
            query: Requête de recherche
            value: Valeur à cacher
            ttl: Durée de vie custom (secondes), sinon utilise default_ttl
            **kwargs: Paramètres de recherche

        Returns:
            Clé de cache générée
        """
        key = self._generate_key(query, **kwargs)

        # Éviction LRU si cache plein
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_lru()

        # Créer ou mettre à jour l'entrée
        now = time.time()
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            accessed_at=now,
            access_count=0,
            ttl=ttl if ttl is not None else self.default_ttl
        )

        self._cache[key] = entry
        self._cache.move_to_end(key)

        logger.debug(f"[SearchCache] SET: {query[:50]}... (ttl={entry.ttl}s)")

        return key

    def invalidate(self, query: str, **kwargs) -> bool:
        """
        Invalide une entrée du cache.

        Args:
            query: Requête de recherche
            **kwargs: Paramètres de recherche

        Returns:
            True si l'entrée existait et a été supprimée
        """
        key = self._generate_key(query, **kwargs)
        return self._remove(key)

    def clear(self) -> int:
        """
        Vide complètement le cache.

        Returns:
            Nombre d'entrées supprimées
        """
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"[SearchCache] Cache vidé: {count} entrées supprimées")
        return count

    def cleanup_expired(self) -> int:
        """
        Nettoie toutes les entrées expirées.

        Returns:
            Nombre d'entrées expirées supprimées
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if self._is_expired(entry)
        ]

        for key in expired_keys:
            self._remove(key)
            self.stats["expirations"] += 1

        if expired_keys:
            logger.info(f"[SearchCache] Nettoyage: {len(expired_keys)} entrées expirées")

        return len(expired_keys)

    def get_stats(self) -> Dict:
        """
        Retourne les statistiques d'utilisation du cache.

        Returns:
            Dict avec hits, misses, hit_rate, size, etc.
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "evictions": self.stats["evictions"],
            "expirations": self.stats["expirations"],
            "total_requests": total_requests,
        }

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Vérifie si une entrée est expirée"""
        if entry.ttl is None:
            return False  # Pas d'expiration

        age = time.time() - entry.created_at
        return age > entry.ttl

    def _remove(self, key: str) -> bool:
        """Supprime une entrée du cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def _evict_lru(self):
        """Éviction LRU: supprime l'entrée la moins récemment utilisée"""
        if not self._cache:
            return

        # OrderedDict: first item = least recently used
        key, entry = self._cache.popitem(last=False)
        self.stats["evictions"] += 1

        logger.debug(f"[SearchCache] LRU éviction: {key} (age={time.time() - entry.created_at:.1f}s)")
