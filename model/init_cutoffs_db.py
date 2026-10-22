"""
Populate public.college_cutoffs in Supabase with branch-level and category-level cutoff ranks
Uses fast batch insertion with execute_values.
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
ALLOTMENTS_CSV = os.path.join(BASE_DIR, 'keam_allotments_clean.csv')

def init_cutoffs():
    print("Connecting to Supabase PostgreSQL with new credentials...")
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

    print("Creating public.college_cutoffs table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS public.college_cutoffs (
            id SERIAL PRIMARY KEY,
            college_id INTEGER REFERENCES public.colleges(id) ON DELETE CASCADE,
            college_code VARCHAR(10) NOT NULL,
            course_code VARCHAR(10) NOT NULL,
            category VARCHAR(10) NOT NULL,
            opening_rank INTEGER NOT NULL,
            closing_rank INTEGER NOT NULL,
            allotted_count INTEGER DEFAULT 1,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT unique_college_course_cat UNIQUE(college_code, course_code, category)
        );

        CREATE INDEX IF NOT EXISTS idx_cutoffs_filter ON public.college_cutoffs(course_code, category, closing_rank);
        CREATE INDEX IF NOT EXISTS idx_cutoffs_code ON public.college_cutoffs(college_code);

        ALTER TABLE public.college_cutoffs ENABLE ROW LEVEL SECURITY;

        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies WHERE tablename = 'college_cutoffs' AND policyname = 'Allow public select on cutoffs'
            ) THEN
                CREATE POLICY "Allow public select on cutoffs" ON public.college_cutoffs
                FOR SELECT USING (true);
            END IF;
        END $$;

        TRUNCATE TABLE public.college_cutoffs RESTART IDENTITY;
    """)

    df = pd.read_csv(ALLOTMENTS_CSV)
    cutoffs = df.groupby(['college_id', 'college_code', 'course_code', 'candidate_category'])['keam_rank'].agg(
        opening_rank='min',
        closing_rank='max',
        allotted_count='count'
    ).reset_index()

    print(f"Computed {len(cutoffs)} unique (college, course, category) cutoffs. Batch inserting...")

    records = [
        (
            int(row['college_id']),
            str(row['college_code']),
            str(row['course_code']),
            str(row['candidate_category']),
            int(row['opening_rank']),
            int(row['closing_rank']),
            int(row['allotted_count'])
        )
        for _, row in cutoffs.iterrows()
    ]

    insert_sql = """
        INSERT INTO public.college_cutoffs (
            college_id, college_code, course_code, category, opening_rank, closing_rank, allotted_count
        ) VALUES %s
        ON CONFLICT (college_code, course_code, category) DO UPDATE SET
            opening_rank = EXCLUDED.opening_rank,
            closing_rank = EXCLUDED.closing_rank,
            allotted_count = EXCLUDED.allotted_count;
    """

    execute_values(cur, insert_sql, records, page_size=1000)
    print(f"Successfully batch inserted {len(records)} rows into public.college_cutoffs!")

    cur.execute("SELECT count(*) FROM public.college_cutoffs;")
    count = cur.fetchone()[0]
    print(f"Verified total rows in public.college_cutoffs: {count}")

    conn.close()

if __name__ == '__main__':
    init_cutoffs()
