import pathlib
import sys

from loguru import logger

from app.config import PRINT_LOG, ERR_LOG, CAPTURE_STD_ERR
from app.misc import app_dir

log_path = pathlib.Path(app_dir / 'log')
log_path.mkdir(parents=True, exist_ok=True)


def setup():
    if CAPTURE_STD_ERR:
        sys.stderr = open(log_path / ERR_LOG, 'a')
    logger.add(
        sink=log_path / PRINT_LOG,
        format='{time} - {name} - {level} - {message}',
        level="DEBUG")
    logger.info("Program started")


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, in_logger):
        self.logger = in_logger
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.info(line.rstrip())
