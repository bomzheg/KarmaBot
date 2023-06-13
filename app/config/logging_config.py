import logging.config
from contextlib import suppress
from pathlib import Path

import yaml

from app.models.config import LogConfig
from app.utils.log import Logger


logger = Logger(__name__)


def logging_setup(config_path: Path, log_config: LogConfig):
    log_dir = log_config.log_path
    log_dir.mkdir(exist_ok=True)
    with (config_path / "logging.yaml").open("r") as f:
        logging_config = yaml.safe_load(f)
        with suppress(KeyError):
            logging_config['handlers']['file']['filename'] = log_dir / "app.log"
        logging.config.dictConfig(logging_config)
    logger.info("Logging configured successfully")
