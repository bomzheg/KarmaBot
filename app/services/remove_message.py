import asyncio
from contextlib import suppress

from aiogram import types
from aiogram.exceptions import TelegramBadRequest


async def remove_kb(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(TelegramBadRequest):
        await message.edit_reply_markup()


async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(TelegramBadRequest):
        await message.delete()


async def cleanup_command_dialog(message: types.Message, delete_bot_reply: bool):
    """
    Delete command message that triggered bot.
    If delete_bot_reply is True, delete bot reply message.
    """
    with suppress(TelegramBadRequest):
        await message.reply_to_message.delete()

    with suppress(TelegramBadRequest):
        if delete_bot_reply:
            await message.delete()
        else:
            await message.edit_reply_markup()
