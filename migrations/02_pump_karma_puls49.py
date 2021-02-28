import sqlite3

from app.config import db_config

with sqlite3.connect(db_config.db_path) as conn:
    cur = conn.cursor()
    cur.execute("""
        UPDATE user_karma 
        SET karma = karma + 49;
    """)
