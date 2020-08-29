import asyncio
from contextlib import suppress

from aiogram import types
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
                                      MessageToDeleteNotFound)


async def remove_kb_after_sleep(message: types.Message, sleep_time: int):
    await asyncio.sleep(sleep_time)
    with suppress(MessageToEditNotFound, MessageCantBeEdited):
        await message.edit_reply_markup()


async def delete_message(message: types.Message):
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()