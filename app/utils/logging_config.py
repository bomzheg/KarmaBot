import logging.config

import yaml

from app.models.config import Config
from app.utils.log import Logger

logger = Logger(__name__)


def setup(config: Config):
    log_dir = config.log.log_path
    log_dir.mkdir(exist_ok=True)
    with (config.app_dir / "config" / "logging.yaml").open("r") as f:
        logging_config = yaml.safe_load(f)
        logging_config['handlers']['file']['filename'] = log_dir / "app.log"
        logging.config.dictConfig(logging_config)
    logger.info("Logging configured successfully")
