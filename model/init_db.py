"""
Initialize Supabase Database Schema and Populate Colleges Data
Loads credentials from model/.env
"""

import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

# Load .env from the model directory
try:
    from dotenv import load_dotenv
    ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
except ImportError:
    pass

DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-ap-southeast-1.pooler.supabase.com')
DB_PORT = int(os.getenv('SUPABASE_DB_PORT', 6543))
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres.snlvfzvvcawwdrsufxzx')
DB_PASS = os.getenv('SUPABASE_DB_PASSWORD', 'Edu-Cator123')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLLEGES_CSV = os.path.join(BASE_DIR, 'colleges_master.csv')

def init_database():
    print(f"Connecting to Supabase PostgreSQL at {DB_HOST}:{DB_PORT}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=15
    )
    conn.autocommit = True
    cur = conn.cursor()

    print("Creating public.colleges table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS public.colleges (
            id SERIAL PRIMARY KEY,
            college_code VARCHAR(10) NOT NULL UNIQUE,
            college_name TEXT NOT NULL,
            college_type VARCHAR(50) NOT NULL,
            district VARCHAR(100),
            pass_percentage NUMERIC(5,2),
            cutoff_sm INTEGER,
            nba_accredited BOOLEAN DEFAULT FALSE,
            naac_accredited BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_colleges_code ON public.colleges(college_code);
        CREATE INDEX IF NOT EXISTS idx_colleges_type ON public.colleges(college_type);
        
        -- Enable RLS and allow public read
        ALTER TABLE public.colleges ENABLE ROW LEVEL SECURITY;
        
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies WHERE tablename = 'colleges' AND policyname = 'Allow public select on colleges'
            ) THEN
                CREATE POLICY "Allow public select on colleges" ON public.colleges
                FOR SELECT USING (true);
            END IF;
        END $$;
        
        TRUNCATE TABLE public.colleges RESTART IDENTITY CASCADE;
    """)

    # Populate from CSV
    print(f"Loading data from {COLLEGES_CSV}...")
    df = pd.read_csv(COLLEGES_CSV)
    
    insert_sql = """
        INSERT INTO public.colleges (
            id, college_code, college_name, college_type, district, pass_percentage, cutoff_sm, nba_accredited, naac_accredited
        ) VALUES %s
        ON CONFLICT (college_code) DO UPDATE SET
            college_name = EXCLUDED.college_name,
            college_type = EXCLUDED.college_type,
            district = EXCLUDED.district,
            pass_percentage = EXCLUDED.pass_percentage,
            cutoff_sm = EXCLUDED.cutoff_sm,
            nba_accredited = EXCLUDED.nba_accredited,
            naac_accredited = EXCLUDED.naac_accredited;
    """

    records = [
        (
            int(row['id']),
            str(row['college_code']),
            str(row['college_name']),
            str(row['college_type']),
            str(row['district']),
            float(row['pass_percentage']) if pd.notnull(row['pass_percentage']) else None,
            int(row['cutoff_sm']) if pd.notnull(row['cutoff_sm']) else None,
            bool(row['nba_accredited']),
            bool(row['naac_accredited'])
        )
        for _, row in df.iterrows()
    ]

    execute_values(cur, insert_sql, records, page_size=1000)
    print(f"Successfully inserted/updated {len(records)} colleges into public.colleges!")

    cur.execute("SELECT count(*) FROM public.colleges;")
    count = cur.fetchone()[0]
    print(f"Total rows in public.colleges: {count}")

    conn.close()

if __name__ == '__main__':
    init_database()
