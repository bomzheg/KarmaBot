import io
import json
import typing

from aiogram import types
from aiogram.types import ChatActions, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import hbold, quote_html
from loguru import logger

from app import config
from app.misc import dp, bot
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma
from app.utils.from_axenia import axenia_raiting
from app.services.user_getter import UserGetter
type_karmas = typing.Tuple[str, typing.Optional[str], float]
type_approve_item = typing.Dict[str, typing.Union[str, float, types.User]]
approve_cb = CallbackData("approve_import", "chat_id", "index", "y_n")
APPROVE_FILE = "approve.json"
PROBLEMS_FILE = "problems.json"


@dp.message_handler(commands="init_from_axenia", commands_prefix='!', is_superuser=True)
async def init_from_axenia(message: types.Message, chat: Chat):
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    # monkey patch
    chat_id = config.python_scripts_chat or chat.chat_id

    log_users, to_approve, problems = await process_import_users_karmas(await axenia_raiting(chat_id), chat)

    await bot.send_document(
        config.DUMP_CHAT_ID,
        ("import_log.json", io.StringIO(json.dumps(log_users, ensure_ascii=False, indent=2)))
    )

    success_text = 'Список карм пользователей импортирован из Аксении'
    if config.DEBUG_MODE:
        await bot.send_message(
            chat_id=config.DUMP_CHAT_ID,
            text=f"{success_text} в чате {chat.chat_id}",
            disable_web_page_preview=True
        )
    else:
        await message.reply(success_text, disable_web_page_preview=True)
    if problems:
        await send_problems_list(problems, chat.chat_id)
    if to_approve:
        await start_approve_karmas(to_approve, config.DUMP_CHAT_ID)


async def process_import_users_karmas(karmas_list: typing.List[type_karmas], chat: Chat):
    log_users = []
    problems = []
    to_approve = []
    async with UserGetter() as user_getter:
        for name, username, karma in karmas_list:
            user = await try_get_user_by_username(username)
            if user is None:
                user_tg = await user_getter.get_user(username, name, chat.chat_id)
                if user_tg is not None:
                    log_users.append(dict(source=(name, username, karma), found=user_tg.as_json()))
                    user = await User.get_or_create_from_tg_user(user_tg)

            if user is not None:
                if username is not None and username == user.username:
                    await save_karma(user, chat.chat_id, karma)
                else:
                    to_approve.append(
                        dict(name=name, username=username, karma=karma, founded_user=user_tg.as_json())
                    )
            else:
                problems.append((name, username, karma))

    return log_users, to_approve, problems


async def send_problems_list(problems: typing.List[type_karmas], chat_id: int):
    problems_users = get_text_problems_users(problems)

    if config.DEBUG_MODE:
        await bot.send_message(
            chat_id=config.DUMP_CHAT_ID,
            text=problems_users,
            disable_web_page_preview=True
        )
    else:
        await bot.send_message(chat_id, problems_users, disable_web_page_preview=True)


async def try_get_user_by_username(username: typing.Optional[str]) -> typing.Optional[User]:
    if username is None:
        return None
    user = await User.get_or_none(username=username)
    return user


async def save_karma(user: User, chat_id: int, karma: float):
    uk, _ = await UserKarma.get_or_create(user=user, chat_id=chat_id)
    uk.karma = karma
    await uk.save()


async def start_approve_karmas(to_approve: typing.List[type_approve_item], chat_id: int):
    save_approve_list(to_approve)
    await bot.send_message(chat_id, **next_approve(get_element_approve(0), 0, chat_id))


def save_approve_list(to_approve: typing.List[type_approve_item]):
    with open(APPROVE_FILE, "w") as f:
        json.dump(to_approve, f)


def get_element_approve(index: int) -> typing.Optional[type_approve_item]:
    with open(APPROVE_FILE, "r") as f:
        to_approve: typing.List[type_approve_item] = json.load(f)
    try:
        return to_approve[index]
    except IndexError:
        return None


def next_approve(approve_item: type_approve_item, index: int, chat_id: int):
    if approve_item is None:
        return dict(
            text=(
                "Все сомнительные пользователи проверены.\n"
                f"{get_problems_list()}"
            ),
            reply_markup=None
        )
    else:
        return dict(
            text=(
                f"Данные из Аксении: "
                f"{quote_html(approve_item['name'])} "
                f"@{quote_html(approve_item['username'])} "
                f"{hbold(approve_item['karma'])}\n"
                f"Найденный пользователь {approve_item['founded_user']}"
            ),
            reply_markup=get_kb_approve(index, chat_id)
        )


def get_kb_approve(index: int, chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Да", callback_data=approve_cb.new(index=index, chat_id=chat_id, y_n="yes")
        ),
        InlineKeyboardButton(
            text="Нет", callback_data=approve_cb.new(index=index, chat_id=chat_id, y_n="no")
        )
    ]])


@dp.callback_query_handler(approve_cb.filter(y_n="no"), is_superuser=True)
async def not_save(callback_query: types.CallbackQuery, callback_data: dict):
    await callback_query.answer()
    index = callback_data["index"]
    chat_id = callback_data["chat_id"]
    elem = get_element_approve(index)

    save_problems_list((elem['name'], elem['username'], elem['karma']))
    await callback_query.message.edit_text(**next_approve(get_element_approve(index+1), index+1, chat_id))


@dp.callback_query_handler(approve_cb.filter(y_n="no"), is_superuser=True)
async def not_save(callback_query: types.CallbackQuery, callback_data: dict):
    await callback_query.answer()
    index = callback_data["index"]
    chat_id = callback_data["chat_id"]
    elem = get_element_approve(index)

    user = await User.get_or_create_from_tg_user(elem['founded_user'])
    await save_karma(user, chat_id, elem['karma'])
    await callback_query.message.edit_text(**next_approve(get_element_approve(index+1), index+1, chat_id))


def save_problems_list(problem: type_karmas):
    with open(PROBLEMS_FILE, "+") as f:
        problems = json.load(f)
        problems.append(problem)
        f.seek(0)
        json.dump(problems, f)


def get_problems_list() -> str:
    with open(PROBLEMS_FILE, "+") as f:
        problems = json.load(f)
    return get_text_problems_users(problems)


def get_text_problems_users(problems: typing.List[type_karmas]) -> str:
    problems_users = "Список пользователей с проблемами:"
    for name, username, karma in problems:
        problems_users += f"\n{quote_html(name)} @{quote_html(username)} {hbold(karma)}"
    return problems_users
