import sqlite3
import sys
from pathlib import Path

from app.config import load_config


db_config = load_config().db

with (Path(__file__).parent / sys.argv[1]).open() as f:
    sql = f.read()

with sqlite3.connect(db_config.db_path) as conn:
    cur = conn.cursor()
    cur.execute(sql)
