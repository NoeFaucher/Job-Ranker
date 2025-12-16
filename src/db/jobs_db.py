import sqlite3
from typing import List, Dict
from .db_utils import get_connection

def insert_job(job: Dict, db_path: str):
    """Insert a single job dict into the DB."""
    conn = get_connection(db_path=db_path)
    cursor = conn.cursor()

    columns = ",".join(job.keys())
    placeholders = ",".join(["?"] * len(job))

    try:
        cursor.execute(
            f"INSERT INTO jobs ({columns}) VALUES ({placeholders})",
            tuple(job.values())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # Job already exists → ignore
        pass

    conn.close()

def insert_jobs_bulk(jobs: List[Dict], db_path: str):
    """Insert many jobs."""
    conn = get_connection(db_path=db_path)
    cursor = conn.cursor()

    if not jobs:
        return

    columns = ",".join(jobs[0].keys())
    placeholders = ",".join(["?"] * len(jobs[0]))

    data = [tuple(job.values()) for job in jobs]

    try:
        cursor.executemany(
            f"INSERT OR IGNORE INTO jobs ({columns}) VALUES ({placeholders})",
            data
        )
        conn.commit()
    finally:
        conn.close()

def get_all_jobs(db_path: str) -> object:
    """Return all jobs as a DataFrame."""
    # import pandas lazily to avoid requiring it for other DB operations
    import pandas as pd

    conn = get_connection(db_path=db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    conn.close()

    return pd.DataFrame([dict(row) for row in rows])

def get_jobs_by_date(date, db_path: str) -> object:
    """Return all jobs inserted on a specific date as a DataFrame.
    
    Args:
        date: datetime.date object or string in format 'YYYY-MM-DD'
        db_path: Path to the SQLite database
        
    Returns:
        pandas.DataFrame with jobs matching the insertion date
    """
    from datetime import date as date_cls
    import pandas as pd
    
    # Convert datetime.date to string if needed
    if isinstance(date, date_cls):
        date_str = date.isoformat()
    else:
        date_str = str(date)
    
    conn = get_connection(db_path=db_path)
    cursor = conn.cursor()
    
    # Query jobs inserted on the specific date
    cursor.execute(
        "SELECT * FROM jobs WHERE inserted_at LIKE ? ORDER BY inserted_at DESC",
        (f"{date_str}%",)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return pd.DataFrame([dict(row) for row in rows])

def update_jobs_bulk(rows: List[Dict], db_path: str):
    """
    Bulk-update rows in the `jobs` table.
    Each dict must contain 'id'. Other keys will be updated.
    """
    if not rows:
        return

    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        for row in rows:
            if "id" not in row:
                raise ValueError(f"Row missing 'id': {row}")

            row_id = row["id"]

            # Columns to update
            update_cols = [col for col in row.keys() if col != "id"]
            if not update_cols:
                continue  # nothing to update

            # SQL: col1=?, col2=?, ...
            set_clause = ", ".join([f"{col} = ?" for col in update_cols])

            sql = f"UPDATE jobs SET {set_clause} WHERE id = ?"

            # Values: [val1, val2, ..., id]
            values = [row[col] for col in update_cols] + [row_id]

            cursor.execute(sql, values)

        conn.commit()
    finally:
        conn.close()
