from pathlib import Path

from app.models.config import LogConfig


def load_log_config(app_dir: Path) -> LogConfig:
    return LogConfig(
        log_chat_id=-1001404337089,
        log_path=app_dir / "log",
    )
