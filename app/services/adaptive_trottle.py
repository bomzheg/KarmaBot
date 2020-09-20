import asyncio
import functools
import typing
from time import time

from aiogram.utils.exceptions import Throttled
DEFAULT_RATE = 0.1


class AdaptiveThrottle:
    def __init__(self, rate=DEFAULT_RATE):
        self.default_rate = rate
        self.last_calls = {}

    def adaptive_throttle(
            self,
            rate: typing.Union[float, int] = None,
            key: str = None,
            chat_id: int = None,
            user_id: int = None,
            on_throttled: typing.Optional[typing.Callable] = None
    ):
        def decorator(func):
            current_key = key if key is not None else func.__name__
            rates = self.get_throttle_dict(chat_id, user_id)
            rates[current_key] = rate

            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                if self.check_time_throttle(rate, current_key, chat_id, user_id):
                    self.update_last_call(current_key)
                    return await func(*args, **kwargs)
                else:
                    if on_throttled:
                        if asyncio.iscoroutinefunction(on_throttled):
                            await on_throttled()
                        else:
                            on_throttled()
                    else:
                        raise Throttled(key=current_key, chat_id=chat_id, user_id=user_id)

            return wrapped
        return decorator

    def get_bucket(self, chat_id: typing.Optional[int], user_id: typing.Optional[int]):
        return self.last_calls.setdefault(chat_id, {}).setdefault(user_id, {})

    def set_bucket(self, chat_id: typing.Optional[int], user_id: typing.Optional[int], bucket: dict):
        self.last_calls.setdefault(chat_id, {})[user_id] = bucket

    def check_time_throttle(self, rate: int, key: str, chat_id: int, user_id: int):
        now = time()
        bucket = self.get_bucket(chat_id, user_id)
        last = bucket.setdefault(key, now)
        self.set_bucket(chat_id, user_id, bucket)
        delta = now - last
        return delta > rate or delta <= 0

    def update_last_call(self, key):
        self.last_calls[key] = time()
