"""
Database connection management for Supabase PostgreSQL.

Provides connection pooling and helper functions for database operations.
"""

from supabase import create_client, Client
from typing import Optional
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Load environment variables
# Try to find .env automatically (works in both dev and Docker)
env_file = find_dotenv()
if env_file:
    load_dotenv(dotenv_path=env_file)
    logger.info(f"[Config] Loaded .env from: {env_file}")
else:
    # Fallback: try common locations
    possible_paths = [
        Path("/app/.env"),  # Docker: /app/.env
        Path(__file__).resolve().parent.parent / ".env",  # Docker: /app/.env
        Path(__file__).resolve().parents[2] / ".env",  # Dev: src/backend -> src -> ShortlistAI
        Path.cwd() / ".env",  # Current working directory
    ]
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            logger.info(f"[Config] Loaded .env from: {env_path}")
            break
    else:
        logger.warning("[Config] No .env file found, using environment variables")

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

