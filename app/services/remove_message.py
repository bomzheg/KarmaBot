import asyncio
from contextlib import suppress

from aiogram import types
from aiogram.exceptions import (TelegramNotFound, TelegramUnauthorizedError)


async def remove_kb(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(TelegramNotFound, TelegramUnauthorizedError):
        await message.edit_reply_markup()


async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(TelegramNotFound, TelegramUnauthorizedError):
        await message.delete()
