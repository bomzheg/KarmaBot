import sqlite3

from app.config import DB_PATH

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute("""
        UPDATE user_karma 
        SET karma = karma + 49;
    """)