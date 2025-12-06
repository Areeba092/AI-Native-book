#!/usr/bin/env python
"""
Interactive database CLI tool for Neon PostgreSQL.

Usage:
    python db_cli.py "SELECT * FROM users"
    python db_cli.py --help
    python db_cli.py --interactive
"""

import asyncio
import sys
import argparse
from src.config import Settings
import asyncpg


class DatabaseCLI:
    """Interactive database CLI."""
    
    def __init__(self):
        self.settings = Settings()
        self.db_url = self.settings.get_database_url
        self.conn = None
    
    async def connect(self):
        """Connect to database."""
        if not self.db_url:
            print("❌ ERROR: DATABASE_URL not set in .env file")
            return False
        
        try:
            self.conn = await asyncpg.connect(self.db_url)
            print("✅ Connected to Neon database")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from database."""
        if self.conn:
            await self.conn.close()
            print("✅ Disconnected")
    
    async def execute_query(self, query: str):
        """Execute a SQL query."""
        if not self.conn:
            print("❌ Not connected to database")
            return
        
        try:
            if query.strip().upper().startswith("SELECT"):
                result = await self.conn.fetch(query)
                if result:
                    print(f"✅ Query returned {len(result)} rows:")
                    for row in result:
                        print(f"  {dict(row)}")
                else:
                    print("✅ Query returned 0 rows")
            else:
                result = await self.conn.execute(query)
                print(f"✅ Query executed: {result}")
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    async def run_interactive(self):
        """Run interactive mode."""
        print("\n🗄️  Interactive Database CLI")
        print("=" * 50)
        print("Commands:")
        print("  .tables          - Show all tables")
        print("  .exit            - Exit")
        print("  .quit            - Exit")
        print("=" * 50)
        
        if not await self.connect():
            return
        
        try:
            while True:
                try:
                    query = input("\nsql> ").strip()
                    
                    if not query:
                        continue
                    
                    if query.lower() in [".exit", ".quit"]:
                        break
                    
                    if query.lower() == ".tables":
                        tables = await self.conn.fetch(
                            """SELECT table_name FROM information_schema.tables 
                               WHERE table_schema='public'"""
                        )
                        print(f"Tables: {[t['table_name'] for t in tables]}")
                        continue
                    
                    await self.execute_query(query)
                
                except KeyboardInterrupt:
                    print("\n\n👋 Interrupted")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        finally:
            await self.disconnect()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database CLI for Neon PostgreSQL"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="SQL query to execute"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    cli = DatabaseCLI()
    
    if args.interactive or not args.query:
        await cli.run_interactive()
    else:
        if await cli.connect():
            await cli.execute_query(args.query)
            await cli.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
