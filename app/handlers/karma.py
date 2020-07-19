import typing

from aiogram import types
from aiogram.types import ChatActions
from aiogram.utils.markdown import hbold, quote_html
from loguru import logger
from pyrogram.errors import RPCError

from app import config
from app.misc import dp, bot
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma
from app.services.trottling import throttling
from app.utils.exeptions import UserWithoutUserIdError
from app.utils.from_axenia import axenia_raiting
from app.services.user_getter import user_getter


@dp.message_handler(commands=["top"], commands_prefix='!')
async def get_top(message: types.Message, chat: Chat):
    parts = message.text.split(' ')
    if not await throttling.set_chat_command(parts[0], chat.chat_id):
        return
    if len(parts) > 1:
        chat = await Chat.get(chat_id=int(parts[1]))
    text_list = ""
    for user, karma in await chat.get_top_karma_list():
        text_list += f"\n{user.mention_no_link} {hbold(karma)}"
    if text_list == "":
        text = "Никто в чате не имеет кармы"
    else:
        text = "Список самых почётных пользователей чата:" + text_list
    await message.reply(text, disable_web_page_preview=True)


how_change = {
    +1: 'увеличил',
    -1: 'уменьшил'
}


def can_change_karma(target_user: User, user: User):
    return user.id != target_user.id


@dp.message_handler(karma_change=True)
@dp.message_handler(karma_change=True, content_types=types.ContentType.STICKER)
async def karma_change(message: types.Message, karma: dict, user: User, chat: Chat):
    # можно заменить на karma['karma_change']
    if not await throttling.set_user_command("karma_change", chat.chat_id, user.tg_id):
        err_text = "Вы слишком часто меняете карму"
        if config.DEBUG_MODE:
            await message.forward(config.DUMP_CHAT_ID)
            return await bot.send_message(chat_id=config.DUMP_CHAT_ID, text=err_text)
        return await message.reply(err_text)
    try:
        target_user = await User.get_or_create_from_tg_user(karma['user'])
    except UserWithoutUserIdError as e:
        e.user_id = user.tg_id
        e.chat_id = chat.chat_id
        e.username = user.username
        e.text = (
            "Обычно так бывает, когда бот в чате недавно и ещё не видел "
            "пользователя, которому плюсанули в виде '+ @username'.",
        )
        raise e
    if not can_change_karma(target_user, user):
        return

    uk, _ = await UserKarma.get_or_create(
        user=target_user,
        chat=chat
    )
    await uk.change(user_changed=user, how_change=karma['karma_change'])
    from_user_karma = await user.get_karma(chat)
    return_text = (
        f"{user.mention_no_link} ({hbold(from_user_karma)}) "
        f"{how_change[karma['karma_change']]} карму пользователю "
        f"{target_user.mention_no_link} ({hbold(uk.karma_round)})"
    )
    if config.DEBUG_MODE:
        await message.forward(config.DUMP_CHAT_ID)
        return await bot.send_message(
            chat_id=config.DUMP_CHAT_ID,
            text=return_text,
            disable_web_page_preview=True
        )
    await message.reply(return_text, disable_web_page_preview=True)


@dp.message_handler(commands="init_from_axenia", commands_prefix='!', is_superuser=True)
async def init_from_axenia(message: types.Message, chat: Chat):
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    python_scripts_chat = -1001399056118
    # mankie patch
    chat_id = python_scripts_chat or chat.chat_id
    karmas_list = await axenia_raiting(chat_id)
    problems = []
    for name, username, karma in karmas_list:
        user = await user_by_name_username(username, name, chat_id)

        if user is not None:
            uk, _ = await UserKarma.get_or_create(user=user, chat=chat)
            uk.karma = karma
            await uk.save()
        else:
            problems.append((name, username, karma))

    success_text = 'Список карм пользователей импортирован из Аксении'
    if config.DEBUG_MODE:
        await bot.send_message(
            chat_id=config.DUMP_CHAT_ID,
            text=f"{success_text} в чате {chat.chat_id}",
            disable_web_page_preview=True
        )
    else:
        await message.reply(success_text, disable_web_page_preview=True)
    problems_user = "Список пользователей с проблемами:"
    for name, username, karma in problems:
        problems_user += f"\n{quote_html(name)} @{username} {hbold(karma)}"

    if config.DEBUG_MODE:
        await bot.send_message(
            chat_id=config.DUMP_CHAT_ID,
            text=problems_user
        )
    else:
        await message.reply(problems_user)


async def user_by_name_username(username, name, chat_id) -> typing.Optional[User]:
    async def try_by_name() -> typing.Optional[User]:
        try:
            return await user_by_name(chat_id, name)
        except RPCError:
            return None

    if username is not None:
        try:
            user = await user_by_username(username)
        except RPCError:
            user = await try_by_name()
    else:
        user = await try_by_name()
    return user


async def user_by_name(chat_id, name) -> User:
    user_tg = await user_getter.get_users_by_fullname(chat_id, name)
    user = await User.get_or_create_from_tg_user(user_tg)
    return user


async def user_by_username(username) -> User:
    user_tg = await user_getter.get_user(username)
    user = await User.get_or_create_from_tg_user(user_tg)
    return user
