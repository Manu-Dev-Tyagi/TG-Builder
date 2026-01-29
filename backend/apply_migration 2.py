"""
Database Migration Script
Applies the portfolio columns migration to Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

supabase: Client = create_client(url, key)

print("🔄 Applying migration: Add portfolio columns to final_personas table")
print("-" * 60)

# The SQL migration
migration_sql = """
ALTER TABLE final_personas
ADD COLUMN IF NOT EXISTS role_in_portfolio TEXT,
ADD COLUMN IF NOT EXISTS funnel_stage TEXT,
ADD COLUMN IF NOT EXISTS recommended_platforms JSONB,
ADD COLUMN IF NOT EXISTS notes TEXT;
"""

try:
    # Execute the migration via RPC or direct SQL
    # Supabase Python client doesn't directly support raw SQL execution
    # We'll use the REST API with the service role key
    
    # Using postgrest's rpc() function is the standard approach
    # But for DDL statements, we need to use the service_role key and call via REST
    
    import requests
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # Construct the SQL execution endpoint
    # Supabase provides /rest/v1/rpc/<function_name> but for raw SQL we need pg_admin or SQL endpoint
    
    # Alternative: Check if columns already exist
    response = supabase.table("final_personas").select("*").limit(1).execute()
    
    if response.data:
        sample = response.data[0] if response.data else {}
        
        missing_columns = []
        for col in ["role_in_portfolio", "funnel_stage", "recommended_platforms", "notes"]:
            if col not in sample:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"⚠️  Missing columns detected: {', '.join(missing_columns)}")
            print("\n📋 MANUAL ACTION REQUIRED:")
            print("=" * 60)
            print("Please run this SQL in your Supabase SQL Editor:")
            print("https://supabase.com/dashboard → Your Project → SQL Editor")
            print("\n" + migration_sql)
            print("=" * 60)
            exit(1)
        else:
            print("✅ All required columns already exist!")
            print("\nColumns verified:")
            print("  - role_in_portfolio")
            print("  - funnel_stage")
            print("  - recommended_platforms")
            print("  - notes")
    else:
        # Table is empty, try to insert a test record to check schema
        print("ℹ️  Table is empty, cannot verify columns via data")
        print("\n📋 Please run the migration SQL manually:")
        print("=" * 60)
        print(migration_sql)
        print("=" * 60)
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n📋 MANUAL MIGRATION REQUIRED:")
    print("=" * 60)
    print("Run this SQL in Supabase SQL Editor:")
    print("https://supabase.com/dashboard")
    print("\n" + migration_sql)
    print("=" * 60)
