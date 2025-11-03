"""Simple SQLite storage for tracked job applications."""
import sqlite3
from typing import Optional, Dict
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "jobs.db"

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    job_title TEXT,
    company TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
)
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(CREATE_SQL)
    conn.commit()
    conn.close()


def add_application(job_id: Optional[str], job_title: str, company: str, notes: Optional[str] = None) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO applications (job_id, job_title, company, notes) VALUES (?, ?, ?, ?)",
        (job_id, job_title, company, notes),
    )
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def list_applications() -> Dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, job_id, job_title, company, applied_at, notes FROM applications ORDER BY applied_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "job_id": r[1],
            "job_title": r[2],
            "company": r[3],
            "applied_at": r[4],
            "notes": r[5],
        }
        for r in rows
    ]
