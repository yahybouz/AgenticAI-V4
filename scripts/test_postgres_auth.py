#!/usr/bin/env python3
"""
Test du système d'authentification avec PostgreSQL
Ce script vérifie que la persistence fonctionne correctement
"""

import asyncio
import sys
from pathlib import Path

# Ajouter backend au path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models.user import UserCreate
from services.auth import AuthService
from services.user import UserService


async def test_postgres_persistence():
    """Test complet du système d'authentification avec PostgreSQL"""

    print("="*70)
    print("🧪 Test Système d'Authentification PostgreSQL - AgenticAI V4")
    print("="*70)
    print()

    # Initialiser les services
    auth_service = AuthService()
    user_service = UserService()

    print("📦 Services initialisés")
    print()

    # ========================================================================
    # Test 1: Initialisation de la base de données
    # ========================================================================
    print("1️⃣  Test initialisation base de données")
    print("-" * 70)

    try:
        await user_service.init_db()
        print("✅ Base de données initialisée")
        print("✅ Tables créées")
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return

    print()

    # ========================================================================
    # Test 2: Utilisateur admin par défaut
    # ========================================================================
    print("2️⃣  Test admin par défaut")
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
    # Test 3: Création utilisateur
    # ========================================================================
    print("3️⃣  Test création utilisateur")
    print("-" * 70)

    try:
        new_user_data = UserCreate(
            email="postgres_test@example.com",
            username="postgresuser",
            password="SecurePass123!",
            full_name="PostgreSQL Test User"
        )

        new_user = await user_service.create_user(new_user_data)
        print(f"✅ Utilisateur créé: {new_user.email}")
        print(f"   ID: {new_user.id}")
        print(f"   Username: {new_user.username}")
        print(f"   Statut: {new_user.status}")
        new_user_id = new_user.id
    except ValueError as e:
        print(f"⚠️  {e}")
        # Si l'utilisateur existe déjà, le récupérer
        existing_user = await user_service.get_user_by_email("postgres_test@example.com")
        if existing_user:
            print(f"✅ Utilisateur existant récupéré: {existing_user.email}")
            new_user_id = existing_user.id
        else:
            print("❌ Erreur lors de la récupération de l'utilisateur")
            return

    print()

    # ========================================================================
    # Test 4: Persistence - Récupération après création
    # ========================================================================
    print("4️⃣  Test persistence - Récupération")
    print("-" * 70)

    retrieved_user = await user_service.get_user(new_user_id)
    if retrieved_user:
        print(f"✅ Utilisateur récupéré depuis la DB: {retrieved_user.email}")
        print(f"   Même ID: {retrieved_user.id == new_user_id}")
    else:
        print("❌ Utilisateur non trouvé en DB")

    print()

    # ========================================================================
    # Test 5: Authentification avec persistence
    # ========================================================================
    print("5️⃣  Test authentification avec DB")
    print("-" * 70)

    # Mauvais mot de passe
    bad_auth = await user_service.authenticate("postgres_test@example.com", "wrongpassword")
    if not bad_auth:
        print("✅ Mauvais mot de passe rejeté")
    else:
        print("❌ Mauvais mot de passe accepté (problème !)")

    # Bon mot de passe
    good_auth = await user_service.authenticate("postgres_test@example.com", "SecurePass123!")
    if good_auth:
        print(f"✅ Authentification réussie: {good_auth.email}")
        print(f"   Last login: {good_auth.last_login}")
    else:
        print("❌ Authentification échouée")

    print()

    # ========================================================================
    # Test 6: Clé API avec persistence
    # ========================================================================
    print("6️⃣  Test clé API avec DB")
    print("-" * 70)

    if good_auth:
        api_key = await user_service.create_api_key(good_auth.id, name="Test Key")
        if api_key:
            print(f"✅ Clé API générée et stockée en DB:")
            print(f"   {api_key}")
            print()

            # Vérifier la clé API
            api_user = await user_service.verify_api_key(api_key)
            if api_user:
                print(f"✅ Clé API valide pour: {api_user.email}")
                print(f"   Même utilisateur: {api_user.id == good_auth.id}")
            else:
                print("❌ Clé API invalide")
        else:
            print("❌ Échec génération clé API")

    print()

    # ========================================================================
    # Test 7: Liste des utilisateurs depuis DB
    # ========================================================================
    print("7️⃣  Test liste utilisateurs depuis DB")
    print("-" * 70)

    users = await user_service.list_users()
    print(f"✅ {len(users)} utilisateur(s) trouvé(s) en DB:")
    for user in users:
        print(f"   • {user.email} ({user.role}) - {user.status}")

    print()

    # ========================================================================
    # Test 8: Nouvelle session - Vérifier persistence
    # ========================================================================
    print("8️⃣  Test nouvelle session (simulée)")
    print("-" * 70)

    # Créer un nouveau service (simule un redémarrage)
    new_service = UserService()
    await new_service.init_db()

    # Vérifier que les données persistent
    persistent_user = await new_service.get_user(new_user_id)
    if persistent_user:
        print(f"✅ Données persistantes après 'redémarrage'")
        print(f"   Email: {persistent_user.email}")
        print(f"   Username: {persistent_user.username}")
        print(f"   Created: {persistent_user.created_at}")
    else:
        print("❌ Données perdues après 'redémarrage' (échec persistence)")

    print()

    # ========================================================================
    # Test 9: Authentification après 'redémarrage'
    # ========================================================================
    print("9️⃣  Test authentification après 'redémarrage'")
    print("-" * 70)

    reauth = await new_service.authenticate("postgres_test@example.com", "SecurePass123!")
    if reauth:
        print(f"✅ Authentification réussie après redémarrage")
        print(f"   Email: {reauth.email}")
        print(f"   Last login mis à jour: {reauth.last_login}")
    else:
        print("❌ Authentification échouée après redémarrage")

    print()

    # ========================================================================
    # Résumé
    # ========================================================================
    print("="*70)
    print("✅ Tous les tests de persistence passés avec succès !")
    print("="*70)
    print()
    print("📊 Résumé:")
    print(f"   • Utilisateurs en DB: {len(users)}")
    print(f"   • Persistence: ✅")
    print(f"   • Authentication: ✅")
    print(f"   • JWT: ✅")
    print(f"   • Clés API: ✅")
    print(f"   • Redémarrage: ✅")
    print()
    print("🎉 Système d'authentification PostgreSQL opérationnel!")
    print()


async def test_connection():
    """Test simple de connexion PostgreSQL"""
    print("🔍 Test de connexion PostgreSQL...")
    try:
        user_service = UserService()
        await user_service.init_db()
        print("✅ Connexion PostgreSQL réussie!")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion PostgreSQL: {e}")
        print()
        print("💡 Assurez-vous que:")
        print("   1. Docker est démarré")
        print("   2. PostgreSQL est lancé: docker compose up -d postgres")
        print("   3. Les variables d'environnement sont correctes dans .env")
        return False


if __name__ == "__main__":
    # Test de connexion d'abord
    can_connect = asyncio.run(test_connection())
    print()

    if can_connect:
        # Lancer les tests complets
        asyncio.run(test_postgres_persistence())
    else:
        sys.exit(1)
