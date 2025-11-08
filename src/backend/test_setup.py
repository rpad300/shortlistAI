"""
Test script to verify backend setup is correct.

Run this before starting the server to ensure all dependencies
and configurations are working.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("ShortlistAI Backend Setup Test")
print("=" * 60)

# Test 1: Configuration
print("\n1. Testing configuration...")
try:
    from config import settings
    print(f"   [OK] Config loaded successfully")
    print(f"   - Environment: {settings.app_env}")
    print(f"   - Port: {settings.app_port}")
    print(f"   - Supabase URL: {'SET' if settings.supabase_url else 'NOT SET'}")
    print(f"   - Gemini API: {'SET' if settings.gemini_api_key else 'NOT SET'}")
except Exception as e:
    print(f"   [ERROR] Config error: {e}")
    sys.exit(1)

# Test 2: Database connection
print("\n2. Testing database connection...")
try:
    from database import get_supabase_client
    client = get_supabase_client()
    
    # Try a simple query
    result = client.table("candidates").select("id").limit(1).execute()
    print(f"   [OK] Supabase connected successfully")
    print(f"   - Can query candidates table")
except Exception as e:
    print(f"   [WARN] Database connection failed: {str(e)[:50]}...")
    print(f"   - This is OK if SUPABASE_SERVICE_ROLE_KEY is not set yet")

# Test 3: AI Services
print("\n3. Testing AI services...")
try:
    from services.ai import get_ai_manager
    ai_manager = get_ai_manager()
    print(f"   [OK] AI Manager initialized")
    print(f"   - Available providers: {list(ai_manager.providers.keys())}")
    print(f"   - Default provider: {ai_manager.default_provider or 'None'}")
except Exception as e:
    print(f"   [WARN] AI services error: {str(e)[:50]}...")
    print(f"   - This is OK if no AI API keys are set yet")

# Test 4: Import all routers
print("\n4. Testing API routers...")
try:
    from routers import interviewer, candidate
    print(f"   [OK] Routers imported successfully")
    print(f"   - Interviewer router: {interviewer.router.prefix}")
    print(f"   - Candidate router: {candidate.router.prefix}")
except Exception as e:
    print(f"   [ERROR] Router import error: {e}")
    sys.exit(1)

# Test 5: Models
print("\n5. Testing data models...")
try:
    from models import CandidateCreate
    test_candidate = CandidateCreate(
        email="test@example.com",
        name="Test User",
        consent_given=True
    )
    print(f"   [OK] Models working correctly")
except Exception as e:
    print(f"   [ERROR] Model error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] Backend setup test PASSED!")
print("=" * 60)
print("\nYou can now start the server with:")
print("   python main.py")
print("\nAPI docs will be available at:")
print("   http://localhost:8000/api/docs")
print("=" * 60)

