import sqlite3

DB_NAME = "quiz.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id TEXT PRIMARY KEY,
        name TEXT,
        total_score INTEGER DEFAULT 0,
        last_activity DATETIME
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS answers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        question_id INTEGER,
        correct INTEGER,
        answered_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS current_question(
        user_id TEXT PRIMARY KEY,
        question_id INTEGER,
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
