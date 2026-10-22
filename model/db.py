"""
Supabase PostgreSQL Database Connection & Query Module for Edu-Cater
Loads credentials automatically from model/.env
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

# Load .env from the model directory
try:
    from dotenv import load_dotenv
    ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'model', '.env')
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
except ImportError:
    pass

# Database Configuration with environment fallbacks
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-ap-southeast-1.pooler.supabase.com')
DB_PORT = int(os.getenv('SUPABASE_DB_PORT', 6543))
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres.snlvfzvvcawwdrsufxzx')
DB_PASS = os.getenv('SUPABASE_DB_PASSWORD', 'Edu-Cator123')
DATABASE_URL = os.getenv('DATABASE_URL', f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def get_connection(autocommit: bool = True):
    """
    Establish and return a new psycopg2 connection to Supabase PostgreSQL.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=15
    )
    conn.autocommit = autocommit
    return conn

@contextmanager
def get_db_cursor(dict_cursor: bool = True):
    """
    Context manager that yields a cursor and automatically handles connection lifecycle.
    """
    conn = get_connection(autocommit=True)
    cursor_factory = RealDictCursor if dict_cursor else None
    cur = conn.cursor(cursor_factory=cursor_factory)
    try:
        yield cur
    finally:
        cur.close()
        conn.close()

def test_connection() -> bool:
    """
    Verify Supabase connection health and count records.
    """
    try:
        with get_db_cursor(dict_cursor=False) as cur:
            cur.execute("SELECT count(*) FROM public.colleges;")
            c_count = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM public.college_cutoffs;")
            cut_count = cur.fetchone()[0]
            print(f"[Supabase DB Connected Successfully]")
            print(f" - Host: {DB_HOST}:{DB_PORT}")
            print(f" - public.colleges: {c_count} rows")
            print(f" - public.college_cutoffs: {cut_count} rows")
            return True
    except Exception as e:
        print(f"[Supabase DB Connection Failed]: {e}")
        return False

def get_colleges_by_ids(college_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Fetch full college rows from public.colleges matching the provided IDs.
    Preserves input order if possible.
    """
    if not college_ids:
        return []
    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute(
            "SELECT * FROM public.colleges WHERE id = ANY(%s);",
            (college_ids,)
        )
        rows = cur.fetchall()
        id_order = {cid: idx for idx, cid in enumerate(college_ids)}
        rows.sort(key=lambda r: id_order.get(r['id'], 999))
        return [dict(r) for r in rows]

def query_eligible_colleges(
    course_code: str,
    category: str,
    keam_rank: int,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Query colleges where closing cutoff rank >= keam_rank
    (i.e., candidate's rank falls inside the admitted cutoff range for that course & quota).
    """
    sql = """
        SELECT 
            c.id AS college_id,
            c.college_code,
            c.college_name,
            c.college_type,
            c.district,
            c.pass_percentage,
            c.nba_accredited,
            c.naac_accredited,
            cut.course_code,
            cut.category,
            cut.opening_rank,
            cut.closing_rank
        FROM public.college_cutoffs cut
        JOIN public.colleges c ON c.id = cut.college_id
        WHERE cut.course_code = %s
          AND cut.category = %s
          AND cut.closing_rank >= %s
        ORDER BY cut.closing_rank ASC
        LIMIT %s;
    """
    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute(sql, (course_code.upper(), category.upper(), keam_rank, limit))
        return [dict(r) for r in cur.fetchall()]

def query_colleges_by_type(college_type: str) -> List[Dict[str, Any]]:
    """
    Fetch all colleges of a given type: 'government', 'autonomous', or 'private'.
    """
    sql = "SELECT * FROM public.colleges WHERE college_type = %s ORDER BY pass_percentage DESC NULLS LAST;"
    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute(sql, (college_type.lower(),))
        return [dict(r) for r in cur.fetchall()]

def query_recommendation_catalog() -> List[Dict[str, Any]]:
    """
    Load college metadata and cutoff statistics for the recommendation engine.
    Category rows are returned with a category value; overall rows have NULL
    category and provide the fallback when a category-specific cutoff is absent.
    """
    sql = """
        WITH category_stats AS (
            SELECT
                college_id,
                course_code,
                category,
                MIN(opening_rank) AS opening_rank,
                MAX(closing_rank) AS closing_rank
            FROM public.college_cutoffs
            GROUP BY college_id, course_code, category
        ),
        overall_stats AS (
            SELECT
                college_id,
                course_code,
                MIN(opening_rank) AS opening_rank,
                MAX(closing_rank) AS closing_rank
            FROM public.college_cutoffs
            GROUP BY college_id, course_code
        )
        SELECT
            c.id,
            c.college_code,
            c.college_name,
            c.college_type,
            c.district,
            c.pass_percentage,
            c.nba_accredited,
            c.naac_accredited,
            stats.course_code,
            stats.category,
            stats.opening_rank,
            stats.closing_rank
        FROM category_stats AS stats
        JOIN public.colleges AS c ON c.id = stats.college_id

        UNION ALL

        SELECT
            c.id,
            c.college_code,
            c.college_name,
            c.college_type,
            c.district,
            c.pass_percentage,
            c.nba_accredited,
            c.naac_accredited,
            stats.course_code,
            NULL AS category,
            stats.opening_rank,
            stats.closing_rank
        FROM overall_stats AS stats
        JOIN public.colleges AS c ON c.id = stats.college_id;
    """
    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute(sql)
        return [dict(row) for row in cur.fetchall()]

if __name__ == '__main__':
    print("Testing Supabase Database connection from Dama Mining/db.py...")
    test_connection()
    print("\nSample Query: Eligible 'CS' colleges for rank 10000 under 'GN' quota:")
    results = query_eligible_colleges(course_code='CS', category='GN', keam_rank=10000, limit=5)
    for r in results:
        print(f" - [{r['college_type']}] {r['college_name']} ({r['district']}) | Cutoff: {r['closing_rank']}")
