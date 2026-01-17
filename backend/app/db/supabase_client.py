"""
Supabase Client for ISAVS
Uses Supabase REST API for database operations
"""
from supabase import create_client, Client
from app.core.config import settings

_supabase_client: Client | None = None

def get_supabase() -> Client:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    return _supabase_client

def init_supabase() -> bool:
    """Initialize and test Supabase connection."""
    try:
        client = get_supabase()
        # Test connection by querying students table
        client.table('students').select('id').limit(1).execute()
        print("✅ Supabase connection successful")
        return True
    except Exception as e:
        print(f"⚠️ Supabase connection warning: {e}")
        return False
