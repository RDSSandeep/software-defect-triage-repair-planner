import sqlite3
import os

DB_PATH = "bugs.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Main table (fresh install)
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

    # Migration safety (older DBs)
    cursor.execute("PRAGMA table_info(bugs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "priority" not in columns:
        cursor.execute("ALTER TABLE bugs ADD COLUMN priority TEXT")

    conn.commit()
    conn.close()


def reset_db():
    """Use ONLY for debugging if DB is broken"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)