import sqlite3
from pathlib import Path
from typing import Optional, Union

def get_connection(db_path: Union[str, Path]):
    """Return a sqlite3 connection.
    """
    db_path = Path(db_path)
    # Create parent directories if they don't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Union[str, Path]):
    """Create the jobs table if it doesn't exist.
    """
    conn = get_connection(db_path=db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            site TEXT,
            job_url TEXT,
            job_url_direct TEXT,
            title TEXT,
            company TEXT,
            location TEXT,
            date_posted TEXT,
            job_type TEXT,
            salary_source TEXT,
            interval TEXT,
            min_amount REAL,
            max_amount REAL,
            currency TEXT,
            is_remote INTEGER,
            job_level TEXT,
            job_function TEXT,
            listing_type TEXT,
            emails TEXT,
            description TEXT,
            company_industry TEXT,
            company_url TEXT,
            company_logo TEXT,
            company_url_direct TEXT,
            company_addresses TEXT,
            company_num_employees INTEGER,
            company_revenue TEXT,
            company_description TEXT,
            skills TEXT,
            experience_range TEXT,
            company_rating REAL,
            company_reviews_count INTEGER,
            vacancy_count INTEGER,
            work_from_home_type TEXT,
            ai_score REAL,
            ai_skills_required TEXT,
            inserted_at TEXT DEFAULT (DATE('now'))
        );
    """)

    conn.commit()
    conn.close()