import asyncio
import functools
import typing
from datetime import datetime, timedelta

from aiogram import types
from aiogram.utils.exceptions import Throttled
from loguru import logger

from app.models import User, Chat

DEFAULT_RATE = 1


class AdaptiveThrottle:
    def __init__(self):
        self.last_calls = {}

    def throttled(
            self,
            rate: typing.Union[float, int] = DEFAULT_RATE,
            key: str = None,
            on_throttled: typing.Optional[typing.Callable] = None
    ):
        rate = timedelta(seconds=rate)

        def decorator(func):
            current_key = key if key is not None else func.__name__

            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                chat: Chat = kwargs['chat']
                user: User = kwargs['user']
                target: User = kwargs['target']
                message: types.Message = args[0]

                if self.check_time_throttle(message.date, rate, current_key, chat.chat_id, user.tg_id, target.tg_id):
                    return await func(*args, **kwargs)
                else:
                    await process_on_throttled(on_throttled, current_key, rate, *args, **kwargs)

            return wrapped
        return decorator

    def check_time_throttle(
            self,
            call_at: datetime,
            rate: int,
            key: str,
            chat_id: int,
            user_id: int,
            target_user_id: int
    ):
        logger.debug(
            "check throttle time for chat {chat_id}, user {user_id}, target {target_user_id} and key {key}",
            chat_id=chat_id, user_id=user_id, target_user_id=target_user_id, key=key,
        )

        bucket = self.get_bucket(chat_id, user_id, target_user_id)

        try:
            last = bucket[key]
        except KeyError:
            logger.debug("there is no last call", )
            return True
        finally:
            bucket[key] = call_at

        self.set_bucket(chat_id, user_id, target_user_id, bucket)
        logger.debug("delta is {delta}", delta=call_at - last)
        return call_at - last > rate

    def get_bucket(self, chat_id: int, user_id: int, target_user_id: int):
        return self.last_calls.setdefault(chat_id, {}).setdefault(user_id, {}).setdefault(target_user_id, {})

    def set_bucket(self, chat_id: int, user_id: int, target_user_id: int, bucket: dict):
        self.last_calls.setdefault(chat_id, {}).setdefault(user_id, {})[target_user_id] = bucket


async def process_on_throttled(
        on_throttled: typing.Callable,
        key: str,
        rate: typing.Union[float, int],
        *args,
        **kwargs
):
    if on_throttled:
        if asyncio.iscoroutinefunction(on_throttled):
            await on_throttled(*args, **kwargs)
        else:
            on_throttled(*args, **kwargs)
    else:
        chat: Chat = kwargs['chat']
        user: User = kwargs['user']
        raise Throttled(key=key, rate=rate, chat_id=chat.chat_id, user_id=user.tg_id)
