import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# We need the direct PostgreSQL connection string for DDL operations
# like CREATE TABLE, since the Supabase REST API (used by the Supabase client and keys)
# does not support database schema migrations.
# You can find this in your Supabase Dashboard: Project Settings > Database > Connection string
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

SCHEMA_SQL = """
-- 1. Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create the flows table
CREATE TABLE IF NOT EXISTS flows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id TEXT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    graph JSONB NOT NULL,
    thumbnail TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    forked_from UUID REFERENCES flows(id) ON DELETE SET NULL,
    locked_params JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create a trigger to auto-update updated_at for flows
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trg_flows_updated_at ON flows;
CREATE TRIGGER trg_flows_updated_at
    BEFORE UPDATE ON flows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. Create the node_comments table
CREATE TABLE IF NOT EXISTS node_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flow_id UUID NOT NULL REFERENCES flows(id) ON DELETE CASCADE,
    node_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    author_role VARCHAR(50) DEFAULT 'student',
    body TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Set up basic Row Level Security (RLS) policies (Optional/Recommended)
-- By default tables are not accessible unless explicitly queried by the service role key.
-- Since the backend uses the service key, RLS can be bypassed, but it's good practice to enable it.
-- ALTER TABLE flows ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE node_comments ENABLE ROW LEVEL SECURITY;
"""

def run_migration():
    if not DATABASE_URL:
        print("Error: SUPABASE_DB_URL is not set in the .env file.")
        print("Please add your PostgreSQL connection string to your .env file.")
        print("Example: SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres")
        return

    try:
        print("Connecting to Supabase PostgreSQL database...")
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("Executing schema migration...")
        # Execute the schema SQL
        cur.execute(SCHEMA_SQL)
        
        # Commit the transaction
        conn.commit()
        print("Migration successful! Tables created.")

    except Exception as e:
        print(f"An error occurred during migration: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
