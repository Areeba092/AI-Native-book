#!/usr/bin/env python
"""
Test script to connect to Neon PostgreSQL database and run queries.
"""

import asyncio
import sys
from src.config import Settings
import asyncpg

async def test_connection():
    """Test connection to Neon database."""
    settings = Settings()
    
    db_url = settings.get_database_url
    
    if not db_url:
        print("❌ ERROR: DATABASE_URL not set in .env file")
        return False
    
    print(f"📡 Connecting to database...")
    print(f"   URL: {db_url[:50]}...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✅ Successfully connected to Neon database!")
        
        # Run a simple test query
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Query result: {result}")
        
        # Get database information
        version = await conn.fetchval("SELECT version()")
        print(f"✅ PostgreSQL Version: {version}")
        
        # List tables
        tables = await conn.fetch(
            """SELECT table_name FROM information_schema.tables 
               WHERE table_schema='public'"""
        )
        print(f"✅ Tables in database: {len(tables)}")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)
