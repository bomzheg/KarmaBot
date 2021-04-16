import logging


class Logger(logging.LoggerAdapter):
    def __init__(self, name: str, extra=None):
        super().__init__(logging.getLogger(name), extra or {})

    def log(self, level, msg: str, *args, **kwargs):
        if self.isEnabledFor(level):
            self.logger._log(level, msg.format(*args, **kwargs), ())
