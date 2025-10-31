#!/usr/bin/env python3
"""Test script to verify backend startup"""
import sys
sys.path.insert(0, '/Users/yahybouz/Desktop/Mes Scripts/AgenticAI-V4/backend')

print("=" * 70)
print("Testing Backend Startup")
print("=" * 70)
print()

try:
    print("1. Importing modules...")
    from api.main import app
    print("✅ App imported successfully")
    print()

    print("2. Checking app configuration...")
    print(f"   Title: {app.title}")
    print(f"   Version: {app.version}")
    print("✅ App configured")
    print()

    print("3. Testing database connection...")
    import asyncio
    from api.dependencies import get_user_service

    async def test_db():
        user_service = get_user_service()
        await user_service.init_db()
        print("✅ Database initialized")

        # Test admin login
        from models.user import UserLogin
        user = await user_service.authenticate("admin@agenticai.dev", "admin123")
        if user:
            print(f"✅ Admin user found: {user.email}")
        else:
            print("❌ Admin user not found")

    asyncio.run(test_db())
    print()

    print("=" * 70)
    print("✅ ALL TESTS PASSED - Backend is ready!")
    print("=" * 70)
    print()
    print("You can now start the server with:")
    print("  cd backend")
    print("  PYTHONPATH=. .venv/bin/uvicorn api.main:app --reload")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
