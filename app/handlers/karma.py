from aiogram import types
from aiogram.types import ChatType
from aiogram.utils.markdown import hbold
from loguru import logger

from app.misc import dp
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma


@dp.message_handler(commands=["top"], commands_prefix='!')
@dp.throttled(rate=60 * 5)
async def get_top(message: types.Message, chat: Chat, user: User):
    args = message.get_args()
    if args:
        chat = await Chat.get(chat_id=int(args))
    logger.info("user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id)
    text_list = ""
    user_ids = []
    for user_, karma in await chat.get_top_karma_list():
        text_list += f"\n{user_.mention_no_link} {hbold(karma)}"
        user_ids.append(user_.id)
    if text_list == "":
        text = "Никто в чате не имеет кармы"
    else:
        text = "Список самых почётных пользователей чата:" + text_list

    prev_uk, user_uk, next_uk = await chat.get_neighbours(user)
    if prev_uk.user.id not in user_ids:
        text += "\n..."
        text += f"\n{prev_uk.user.mention_no_link} {hbold(prev_uk.karma_round)}"
    if user_uk.user.id not in user_ids:
        text += f"\n{user_uk.user.mention_no_link} {hbold(user_uk.karma_round)}"
    if next_uk.user.id not in user_ids:
        text += f"\n{next_uk.user.mention_no_link} {hbold(next_uk.karma_round)}"

    await message.reply(text, disable_web_page_preview=True)


@dp.throttled(rate=15)
@dp.message_handler(ChatType.is_group_or_super_group, commands=["me"], commands_prefix='!')
async def get_top(message: types.Message, chat: Chat, user: User):
    logger.info("user {user} ask his karma in chat {chat}", user=user.tg_id, chat=chat.chat_id)
    uk, _ = await UserKarma.get_or_create(chat=chat, user=user)
    await message.reply(f"Ваша карма в данном чате: {uk.karma_round}", disable_web_page_preview=True)


@dp.throttled(rate=15)
@dp.message_handler(ChatType.is_private, commands=["me"], commands_prefix='!')
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
