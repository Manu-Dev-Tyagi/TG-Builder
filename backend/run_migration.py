"""
Direct PostgreSQL Migration Script
Uses psycopg2 to execute DDL statements
"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 is not installed")
    print("Installing psycopg2-binary...")
    import subprocess
    subprocess.check_call(["pip3", "install", "psycopg2-binary"])
    import psycopg2

# Get Supabase connection details
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    print("❌ SUPABASE_URL not found in environment")
    exit(1)

# Extract project reference from URL (format: https://PROJECT_REF.supabase.co)
project_ref = url.replace("https://", "").replace(".supabase.co", "").split("/")[0]

# Supabase PostgreSQL connection string format:
# postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
# The password is the database password (different from API key)

print("⚠️  To connect directly to PostgreSQL, we need your database password.")
print("This is different from your SUPABASE_KEY (API key).")
print("\nYou can find it in: Supabase Dashboard → Project Settings → Database → Password")
print("\nAlternatively, I'll create a migration verification script using the REST API...")

# Since we can't get the DB password programmatically, let's use an alternative approach
# We'll use Supabase's REST API to execute a function that does the migration

migration_sql = """
ALTER TABLE final_personas
ADD COLUMN IF NOT EXISTS role_in_portfolio TEXT,
ADD COLUMN IF NOT EXISTS funnel_stage TEXT,
ADD COLUMN IF NOT EXISTS recommended_platforms JSONB,
ADD COLUMN IF NOT EXISTS notes TEXT;
"""

print("\n" + "="*70)
print("MIGRATION SQL (Copy and paste into Supabase SQL Editor)")
print("="*70)
print(migration_sql)
print("="*70)
print("\nTo apply:")
print("1. Go to: https://supabase.com/dashboard")
print("2. Select your project")
print("3. Click 'SQL Editor' in the left sidebar")
print("4. Click 'New Query'")
print("5. Paste the SQL above")
print("6. Click 'RUN'")
print("\nAfter running, execute: python3 verify_migration.py")
