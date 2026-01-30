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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rsvp (
        user_id INTEGER PRIMARY KEY,
        attending INTEGER DEFAULT 0,
        food TEXT DEFAULT ''
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        user_id INTEGER PRIMARY KEY,
        winner TEXT,
        total_points INTEGER
    )
    """)

    conn.commit()
    conn.close()
