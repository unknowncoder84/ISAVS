"""
Clear all students from database
Run this to delete old HOG embeddings before re-enrolling with DeepFace
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def clear_students():
    """Delete all students from database."""
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("🗑️  Clearing all students from database...")
        
        # Delete all students (cascades to related records)
        response = supabase.table("students").delete().neq("id", 0).execute()
        
        print(f"✅ Deleted all students")
        print(f"   Response: {response}")
        
        # Verify
        count_response = supabase.table("students").select("id", count="exact").execute()
        print(f"✅ Remaining students: {count_response.count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing students: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = clear_students()
    if success:
        print("\n✅ Database cleared successfully!")
        print("⚠️  You can now re-enroll students with the new DeepFace system")
    else:
        print("\n❌ Failed to clear database")
