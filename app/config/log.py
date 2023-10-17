from pathlib import Path

from app.models.config import LogConfig


def load_log_config(app_dir: Path, log_chat_id: int) -> LogConfig:
    return LogConfig(
        log_chat_id=log_chat_id,
        log_path=app_dir / "log",
    )
