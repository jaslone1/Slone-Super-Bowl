import sqlite3
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent / "superbowl.db"


def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def init_db():
    """Initialize database tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            pin TEXT NOT NULL
        )
    """)
    
    # RSVP table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rsvp (
            user_id INTEGER PRIMARY KEY,
            attending INTEGER DEFAULT 0,
            food TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Predictions table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            user_id INTEGER PRIMARY KEY,
            winner TEXT,
            total_points INTEGER,
            first_play TEXT,
            first_commercial TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
