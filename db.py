import sqlite3

def get_connection():
    return sqlite3.connect("superbowl.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        pin TEXT
    )
    """)

    conn.commit()
    conn.close()
