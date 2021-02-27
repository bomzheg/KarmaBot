import asyncio

from aiogram import types
from aiogram.types import ChatType
from aiogram.utils.markdown import hpre
from loguru import logger

from app import config
from app.misc import dp
from app.models import (
    Chat,
    User
)
from app.services.karma import (
    get_top as get_karma_top,
    get_me_info,
    get_me_chat_info
)
from app.services.remove_message import delete_message


@dp.message_handler(commands=["top"], commands_prefix='!', chat_type=types.ChatType.PRIVATE)
@dp.throttled(rate=2)
async def get_top_from_private(message: types.Message, user: User):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        chat = await Chat.get(chat_id=int(parts[1]))
    else:
        return await message.reply(
            "Эту команду можно использовать только в группах "
            "или с указанием id нужного чата, например:"
            "\n" + hpre("!top -1001399056118")
        )
    logger.info("user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id)
    text = await get_karma_top(chat, user)

    await message.reply(text, disable_web_page_preview=True)


@dp.message_handler(commands=["top"], commands_prefix='!')
@dp.throttled(rate=60 * 5)
async def get_top(message: types.Message, chat: Chat, user: User):
    logger.info("user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id)
    text = await get_karma_top(chat, user)

    await message.reply(text, disable_web_page_preview=True)


@dp.message_handler(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP], commands=["me"], commands_prefix='!')
@dp.throttled(rate=15)
async def get_top(message: types.Message, chat: Chat, user: User):
    logger.info("user {user} ask his karma in chat {chat}", user=user.tg_id, chat=chat.chat_id)
    uk, number_in_top = await get_me_chat_info(chat=chat, user=user)
    msg = await message.reply(
        f"Ваша карма в данном чате: <b>{uk.karma:.2f}</b> ({number_in_top})",
        disable_web_page_preview=True
    )
    asyncio.create_task(delete_message(msg, config.TIME_TO_REMOVE_TEMP_MESSAGES))
    asyncio.create_task(delete_message(message, config.TIME_TO_REMOVE_TEMP_MESSAGES))


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=["me"], commands_prefix='!')
@dp.throttled(rate=15)
async def get_top(message: types.Message, user: User):
    logger.info("user {user} ask his karma", user=user.tg_id)
    uks = await get_me_info(user)
    text = ""
    for uk, number_in_top in uks:
        text += f"\n{uk.chat.mention} <b>{uk.karma:.2f}</b> ({number_in_top})"
    if text:
        return await message.reply(
            f"У Вас есть карма в следующих чатах:{text}",
            disable_web_page_preview=True
        )
    await message.reply(
        f"У Вас нет никакой кармы ни в каких чатах",
        disable_web_page_preview=True
    )
