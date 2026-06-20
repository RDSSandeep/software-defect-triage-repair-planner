import sqlite3
import os

# Ensure DB is created in the data/ directory under project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "bug_tracker.db")

def get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            environment TEXT NOT NULL,
            steps TEXT,
            priority TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Safe migration: add priority column to existing databases if absent
    cursor.execute("PRAGMA table_info(bugs)")
    columns = [row[1] for row in cursor.fetchall()]
    if "priority" not in columns:
        cursor.execute("ALTER TABLE bugs ADD COLUMN priority TEXT")

    conn.commit()
    conn.close()
