import asyncio
import functools
import typing
from time import time

from aiogram.utils.exceptions import Throttled


class AdaptiveThrottle:
    def __init__(self, rate=0):
        self.default_rate = rate
        self.rates = {}
        self.last_calls = {}

    def adaptive_throttle(self, rate=None, key=None, on_throttled: typing.Optional[typing.Callable] = None):
        def decorator(func):
            current_key = key if key is not None else func.__name__
            self.rates[current_key] = rate

            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                if self.check_time_throttle(rate, current_key):
                    self.update_last_call(current_key)
                    return await func(*args, **kwargs)
                else:
                    if on_throttled:
                        if asyncio.iscoroutinefunction(on_throttled):
                            await on_throttled()
                        else:
                            on_throttled()
                    else:
                        raise Throttled(key=current_key)

            return wrapped
        return decorator

    def check_time_throttle(self, rate: int, key):
        now = time()
        last = self.last_calls.setdefault(key, now)
        delta = now - last
        return delta > rate or delta <= 0

    def update_last_call(self, key):
        self.last_calls[key] = time()
