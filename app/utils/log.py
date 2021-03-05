from loguru import logger

from app.models.config import LogConfig


def setup(log_config: LogConfig):
    log_config.log_path.mkdir(parents=True, exist_ok=True)
    logger.add(
        sink=log_config.log_file,
        format='{time} - {name} - {level} - {message}',
        level="INFO",
        encoding='utf-8',
    )
    logger.info("Program started")
