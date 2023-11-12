import logging


class Logger(logging.LoggerAdapter):
    def __init__(self, name: str, extra=None):
        super().__init__(logging.getLogger(name), extra or {})

    def log(
        self,
        level,
        msg: str,
        *args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
        **kwargs,
    ):
        if self.isEnabledFor(level):
            # noinspection PyProtectedMember
            self.logger._log(
                level=level,
                msg=msg.format(*args, **kwargs),
                args=tuple(),
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
                stacklevel=stacklevel,
            )
