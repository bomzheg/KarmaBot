import asyncio

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.text_decorations import html_decoration as hd

from app.infrastructure.database.models import User, Chat
from app.infrastructure.database.repo.chat import ChatRepo
from app.models.config import Config
from app.services.karma import (
    get_top as get_karma_top,
    get_me_info,
    get_me_chat_info
)
from app.services.remove_message import delete_message
from app.utils.log import Logger


logger = Logger(__name__)
router = Router(name=__name__)


@router.message(Command("top", prefix='!'), F.chat.type == "private")
async def get_top_from_private(message: types.Message, user: User, chat_repo: ChatRepo):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        chat = await Chat.get(chat_id=int(parts[1]))
    else:
        return await message.reply(
            "Эту команду можно использовать только в группах "
            "или с указанием id нужного чата, например:"
            "\n" + hd.code("!top -1001399056118")
        )
    logger.info("user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id)
    text = await get_karma_top(chat_repo, chat, user)

    await message.reply(text, disable_web_page_preview=True)


@router.message(Command("top", prefix='!'))
async def get_top(message: types.Message, chat: Chat, user: User, chat_repo: ChatRepo):
    logger.info("user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id)
    text = await get_karma_top(chat_repo, chat, user)

    await message.reply(text, disable_web_page_preview=True)


@router.message(F.chat.type.in_(["group", "supergroup"]), Command("me", prefix='!'))
async def get_top(message: types.Message, chat: Chat, user: User, config: Config):
    logger.info("user {user} ask his karma in chat {chat}", user=user.tg_id, chat=chat.chat_id)
    uk, number_in_top = await get_me_chat_info(chat=chat, user=user)
    msg = await message.reply(
        f"Ваша карма в данном чате: <b>{uk.karma:.2f}</b> ({number_in_top})",
        disable_web_page_preview=True
    )
    asyncio.create_task(delete_message(msg, config.time_to_remove_temp_messages))
    asyncio.create_task(delete_message(message, config.time_to_remove_temp_messages))


@router.message(F.chat.type == "private", Command("me", prefix='!'))
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
