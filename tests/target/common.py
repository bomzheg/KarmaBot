import asyncio
import typing

from aiogram import types
from app.filters.has_target import HasTargetFilter


def filter_check(message: types.Message, conf: typing.Dict[str, bool]):
    target_filter = HasTargetFilter(has_target=conf)
    return asyncio.run(target_filter.check(message))
