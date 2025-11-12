"""
Database connection management for Supabase PostgreSQL.

Provides connection pooling and helper functions for database operations.
"""

from supabase import create_client, Client
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")

# Global Supabase client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.
    
    Uses secret key (service role) for backend operations that bypass RLS.
    Supports both new API keys (sb_secret_*) and legacy keys.
    Also accepts typo version SUPABESE_SECRETE_KEY.
    
    Returns:
        Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        
        # Use new secret key (sb_secret_*) - replaces legacy service_role
        supabase_key = (
            os.getenv("SUPABASE_SECRET_KEY") or 
            os.getenv("SUPABESE_SECRETE_KEY") or  # Accept typo version
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Legacy fallback
        )
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing Supabase credentials. "
                "Ensure SUPABASE_URL and SUPABASE_SECRET_KEY are set in .env"
            )
        
        key_preview = supabase_key[:8] + "..." if supabase_key else "(empty)"
        print(f"[Supabase] Connecting to {supabase_url} with key prefix: {key_preview} (length: {len(supabase_key)})")
        _supabase_client = create_client(supabase_url, supabase_key)
    
    return _supabase_client


async def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        client = get_supabase_client()
        # Simple query to verify connection
        result = client.table("candidates").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False

