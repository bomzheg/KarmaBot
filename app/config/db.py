import os
from pathlib import Path

from app.models.config.db import DBConfig, DBType


def load_db_config(app_dir: Path):
    db_config = DBConfig()
    db_config.type_ = DBType(os.getenv("DB_TYPE", default='sqlite'))
    db_config.user = os.getenv("DB_USER")
    db_config.password = os.getenv("DB_PASSWORD")
    db_config.name = os.getenv("DB_NAME")
    db_config.host = os.getenv("DB_HOST", default='localhost')
    db_config.port = os.getenv("DB_PORT")
    db_config.driver = os.getenv("DB_DRIVER")
    db_config.db_path = os.getenv("DB_PATH", default=app_dir / "db_data" / "karma.db")
    return db_config
