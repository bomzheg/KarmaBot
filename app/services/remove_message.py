import asyncio
from contextlib import suppress

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest


async def remove_kb(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(TelegramBadRequest):
        await message.edit_reply_markup()


async def delete_message(message: types.Message, sleep_time: int = 0):
    if sleep_time:
        await asyncio.sleep(sleep_time)

    with suppress(TelegramBadRequest):
        await message.delete()


async def delete_message_by_id(chat_id: int, message_id: int, bot: Bot):
    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id, message_id)


async def cleanup_command_dialog(
    bot_message: types.Message, delete_bot_reply: bool, delay: int = 0
):
    """
    Delete command message that triggered bot.
    If delete_bot_reply is True, delete bot reply message, else remove reply markup.
    """
    if delay:
        await asyncio.sleep(delay)

    await delete_message(bot_message.reply_to_message)

    if delete_bot_reply:
        await delete_message(bot_message)
    else:
        with suppress(TelegramBadRequest):
            await bot_message.edit_reply_markup()
