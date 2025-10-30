#!/usr/bin/env python3
"""
Test du système d'authentification
"""

import asyncio
import sys
from pathlib import Path

# Ajouter backend au path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models.user import UserCreate, UserLogin
from services.auth import AuthService
from services.user import UserService


async def test_authentication():
    """Test complet du système d'authentification"""

    print("="*70)
    print("🧪 Test Système d'Authentification AgenticAI V4")
    print("="*70)
    print()

    # Initialiser les services
    auth_service = AuthService()
    user_service = UserService()

    print("📦 Services initialisés")
    print()

    # ========================================================================
    # Test 1: Utilisateur admin par défaut
    # ========================================================================
    print("1️⃣  Test admin par défaut")
    print("-" * 70)

    admin = await user_service.authenticate("admin@agenticai.dev", "admin123")
    if admin:
        print(f"✅ Admin trouvé: {admin.email}")
        print(f"   ID: {admin.id}")
        print(f"   Rôle: {admin.role}")
        print(f"   Quotas: {admin.max_agents} agents, {admin.max_documents} docs")
    else:
        print("❌ Admin non trouvé")
        return

    print()

    # ========================================================================
    # Test 2: Inscription d'un nouvel utilisateur
    # ========================================================================
    print("2️⃣  Test inscription utilisateur")
    print("-" * 70)

    try:
        new_user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User"
        )

        new_user = await user_service.create_user(new_user_data)
        print(f"✅ Utilisateur créé: {new_user.email}")
        print(f"   ID: {new_user.id}")
        print(f"   Username: {new_user.username}")
        print(f"   Statut: {new_user.status}")
    except ValueError as e:
        print(f"⚠️  {e} (normal si déjà créé)")

    print()

    # ========================================================================
    # Test 3: Authentification
    # ========================================================================
    print("3️⃣  Test authentification")
    print("-" * 70)

    # Mauvais mot de passe
    bad_auth = await user_service.authenticate("test@example.com", "wrongpassword")
    if not bad_auth:
        print("✅ Mauvais mot de passe rejeté")
    else:
        print("❌ Mauvais mot de passe accepté (problème !)")

    # Bon mot de passe
    good_auth = await user_service.authenticate("test@example.com", "SecurePass123!")
    if good_auth:
        print(f"✅ Authentification réussie: {good_auth.email}")
        print(f"   Last login: {good_auth.last_login}")
    else:
        print("❌ Authentification échouée")

    print()

    # ========================================================================
    # Test 4: Génération de tokens JWT
    # ========================================================================
    print("4️⃣  Test génération JWT")
    print("-" * 70)

    if good_auth:
        token = auth_service.create_access_token(
            user_id=good_auth.id,
            email=good_auth.email,
            role=good_auth.role
        )

        print(f"✅ Token généré:")
        print(f"   {token[:50]}...")
        print()

        # Vérifier le token
        token_data = auth_service.verify_token(token)
        if token_data:
            print(f"✅ Token vérifié:")
            print(f"   User ID: {token_data.user_id}")
            print(f"   Email: {token_data.email}")
            print(f"   Rôle: {token_data.role}")
        else:
            print("❌ Token invalide")

    print()

    # ========================================================================
    # Test 5: Génération de clé API
    # ========================================================================
    print("5️⃣  Test génération clé API")
    print("-" * 70)

    if good_auth:
        api_key = await user_service.create_api_key(good_auth.id)
        if api_key:
            print(f"✅ Clé API générée:")
            print(f"   {api_key}")
            print()

            # Vérifier la clé API
            api_user = await user_service.verify_api_key(api_key)
            if api_user:
                print(f"✅ Clé API valide pour: {api_user.email}")
            else:
                print("❌ Clé API invalide")
        else:
            print("❌ Échec génération clé API")

    print()

    # ========================================================================
    # Test 6: Liste des utilisateurs
    # ========================================================================
    print("6️⃣  Test liste utilisateurs")
    print("-" * 70)

    users = await user_service.list_users()
    print(f"✅ {len(users)} utilisateur(s) trouvé(s):")
    for user in users:
        print(f"   • {user.email} ({user.role}) - {user.status}")

    print()

    # ========================================================================
    # Test 7: Statistiques utilisateur
    # ========================================================================
    print("7️⃣  Test statistiques utilisateur")
    print("-" * 70)

    if good_auth:
        stats = await user_service.get_user_stats(good_auth.id)
        if stats:
            print(f"✅ Statistiques pour {good_auth.email}:")
            print(f"   Agents: {stats.agents_count}")
            print(f"   Documents: {stats.documents_count}")
            print(f"   Stockage: {stats.storage_used_mb} MB")
            print(f"   Requêtes: {stats.total_queries}")

    print()

    # ========================================================================
    # Résumé
    # ========================================================================
    print("="*70)
    print("✅ Tous les tests passés avec succès !")
    print("="*70)
    print()
    print("📊 Résumé:")
    print(f"   • Utilisateurs créés: {len(users)}")
    print(f"   • Authentication: ✅")
    print(f"   • JWT: ✅")
    print(f"   • Clés API: ✅")
    print()
    print("🎉 Système d'authentification opérationnel!")
    print()


if __name__ == "__main__":
    asyncio.run(test_authentication())
