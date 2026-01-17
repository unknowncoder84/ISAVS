"""
Quick database connection test script
Run: python test_db_connection.py
"""
import asyncio
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

async def test_connection():
    print("=" * 50)
    print("Testing Database Connection")
    print("=" * 50)
    
    from app.core.config import settings
    print(f"\n📋 Database URL (masked): {settings.DATABASE_URL[:50]}...")
    
    # Test 1: Direct asyncpg connection
    print("\n🔍 Test 1: Direct asyncpg connection...")
    try:
        import asyncpg
        import ssl
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Parse the URL
        url = settings.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgres://")
        
        conn = await asyncpg.connect(url, ssl=ssl_context)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        print(f"   ✅ Direct connection successful! Result: {result}")
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
    
    # Test 2: SQLAlchemy async connection
    print("\n🔍 Test 2: SQLAlchemy async connection...")
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"   ✅ SQLAlchemy connection successful!")
    except Exception as e:
        print(f"   ❌ SQLAlchemy connection failed: {e}")
    
    # Test 3: Check if tables exist
    print("\n🔍 Test 3: Checking if tables exist...")
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"   ✅ Found tables: {', '.join(tables)}")
            else:
                print("   ⚠️ No tables found! Run schema.sql in Supabase SQL Editor")
    except Exception as e:
        print(f"   ❌ Table check failed: {e}")
    
    # Test 4: Supabase REST API
    print("\n🔍 Test 4: Supabase REST API...")
    try:
        from app.db.supabase_client import get_supabase
        client = get_supabase()
        result = client.table('students').select('id').limit(1).execute()
        print(f"   ✅ Supabase REST API working!")
    except Exception as e:
        print(f"   ❌ Supabase REST failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_connection())
