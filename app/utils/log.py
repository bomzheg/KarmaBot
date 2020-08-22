import pathlib

from loguru import logger

from app.config import PRINT_LOG
from app.misc import app_dir

log_path = pathlib.Path(app_dir / 'log')
log_path.mkdir(parents=True, exist_ok=True)


def setup():
    logger.add(
        sink=log_path / PRINT_LOG,
        format='{time} - {name} - {level} - {message}',
        level="INFO",
        encoding='utf-8',
    )
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
