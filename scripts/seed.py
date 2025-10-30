#!/usr/bin/env python3
"""
AgenticAI V4 - Script de seed de la base de données
Initialise les données de base (agents, politiques, etc.)
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents import seed_default_agents
from backend.config import get_settings

async def seed_database():
    """Seed la base de données avec les données initiales."""
    print("🌱 AgenticAI V4 - Seed de la base de données")
    print("=" * 50)

    settings = get_settings()
    print(f"📋 Environnement: {settings.environment}")
    print(f"📋 Version: {settings.api_version}")
    print()

    # 1. Seed agents par défaut
    print("1️⃣  Chargement des agents par défaut...")
    try:
        seed_default_agents()
        print("✅ Agents chargés avec succès")
    except Exception as e:
        print(f"❌ Erreur lors du chargement des agents: {e}")
        return False

    # 2. TODO: Seed politiques d'orchestration
    print("\n2️⃣  Chargement des politiques d'orchestration...")
    print("⏭️  TODO: Implémenter le seed des politiques")

    # 3. TODO: Seed collections Qdrant
    print("\n3️⃣  Initialisation des collections Qdrant...")
    print("⏭️  TODO: Créer les collections vectorielles")

    # 4. TODO: Seed données de test (optionnel)
    print("\n4️⃣  Données de test (optionnel)...")
    print("⏭️  TODO: Ajouter des données de test")

    print("\n" + "=" * 50)
    print("✅ Seed terminé avec succès!")
    print("\nProchaines étapes:")
    print("  1. Démarrer l'API: ./scripts/run-backend.sh")
    print("  2. Tester: curl http://localhost:8000/info")
    print("  3. Docs: http://localhost:8000/docs")

    return True

def main():
    """Point d'entrée principal."""
    try:
        result = asyncio.run(seed_database())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Seed interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
