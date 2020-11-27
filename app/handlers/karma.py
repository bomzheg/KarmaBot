from aiogram import types
from aiogram.types import ChatType
from aiogram.utils.markdown import hbold, hpre
from loguru import logger

from app.misc import dp
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma
from app.services.karma_top import get_karma_top


@dp.message_handler(commands=["top"], commands_prefix='!', chat_type=types.ChatType.PRIVATE)
@dp.throttled(rate=2)
async def get_top_from_private(message: types.Message, chat: Chat, user: User):
    parts = message.text.split(maxsplit=1)
    logger.info("user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id)
    if len(parts) > 1:
        chat = await Chat.get(chat_id=int(parts[1]))
        return await message.reply(
            "Эту команду можно использовать только в группах "
            "или с указанием id нужного чата, например:"
            "\n" + hpre("!top -1001399056118")
        )
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
    uk, _ = await UserKarma.get_or_create(chat=chat, user=user)
    await message.reply(f"Ваша карма в данном чате: {uk.karma_round}", disable_web_page_preview=True)


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=["me"], commands_prefix='!')
@dp.throttled(rate=15)
async def get_top(message: types.Message, user: User):
    logger.info("user {user} ask his karma", user=user.tg_id)
    uks = await UserKarma.filter(user=user).prefetch_related('chat').all()
    text = ""
    for uk in uks:
        text += f"\n{uk.chat.mention} {hbold(uk.karma_round)}"
    if text:
        return await message.reply(
            f"У Вас есть карма в следующих чатах:{text}",
            disable_web_page_preview=True
        )
    await message.reply(
        f"У Вас нет никакой кармы ни в каких чатах",
        disable_web_page_preview=True
    )
