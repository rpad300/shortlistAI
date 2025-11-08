"""
Database package for CV Analysis Platform.

Provides database connection, models, and migrations.
"""

from .connection import get_supabase_client, check_database_connection

__all__ = [
    "get_supabase_client",
    "check_database_connection",
]

