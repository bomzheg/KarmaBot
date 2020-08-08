import io
import json
import typing
from contextlib import suppress

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.markdown import hbold, quote_html

from app import config
from app.misc import dp, bot
from app.models.chat import Chat
from app.models.user import User
from app.models.user_karma import UserKarma
from app.services.user_getter import UserGetter
from app.utils.from_axenia import axenia_raiting

type_karmas = typing.Tuple[str, typing.Optional[str], float]
type_approve_item = typing.Dict[str, typing.Union[str, float, types.User]]
approve_cb = CallbackData("approve_import", "chat_id", "index", "y_n")
processing_text = "Сообщение обрабатывается, выполнено ~{:.2%}"

jsons_path = config.app_dir / "jsons"
jsons_path.mkdir(exist_ok=True, parents=True)
APPROVE_FILE = jsons_path / "approve.json"
PROBLEMS_FILE = jsons_path / "problems.json"


@dp.message_handler(commands="init_from_axenia", commands_prefix='!', is_superuser=True)
async def init_from_axenia(message: types.Message, chat: Chat):
    msg = await message.reply(processing_text.format(-0.1))
    # monkey patch
    chat_id = config.python_scripts_chat or chat.chat_id

    log_users, to_approve, problems = await process_import_users_karmas(await axenia_raiting(chat_id), chat, msg)
    await msg.delete()

    await bot.send_document(
        config.DUMP_CHAT_ID,
        ("import_log.json", io.StringIO(json.dumps(log_users, ensure_ascii=False, indent=2)))
    )

    await message.reply('Список карм пользователей импортирован из Аксении', disable_web_page_preview=True)
    if problems:
        await send_problems_list(problems, chat.chat_id)
    if to_approve:
        await start_approve_karmas(to_approve, config.DUMP_CHAT_ID)


async def process_import_users_karmas(karmas_list: typing.List[type_karmas], chat: Chat, message: types.Message = None):
    """

    :param karmas_list:
    :param chat:
    :param message: by bot in that be outputed percent of completed
    :return:
    """
    if message is not None and message.from_user.id != bot.id:
        message = None
    log_users = []
    problems = []
    to_approve = []
    async with UserGetter() as user_getter:
        for i, karma_elem in enumerate(karmas_list):
            if message is not None and i % 5 == 0:
                with suppress(TelegramAPIError):
                    await message.edit_text(processing_text.format(i/len(karmas_list)))

            name, username, karma = karma_elem
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
    with APPROVE_FILE.open("w") as f:
        json.dump(to_approve, f)
    with PROBLEMS_FILE.open("w") as f:
        json.dump([], f)


def get_element_approve(index: int) -> typing.Optional[type_approve_item]:
    with APPROVE_FILE.open("r") as f:
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
async def not_save_user_karma(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    await callback_query.answer()
    index = int(callback_data["index"])
    chat_id = int(callback_data["chat_id"])
    elem = get_element_approve(index)

    save_problems_list((elem['name'], elem['username'], elem['karma']))
    await callback_query.message.edit_text(**next_approve(get_element_approve(index+1), index+1, chat_id))


@dp.callback_query_handler(approve_cb.filter(y_n="yes"), is_superuser=True)
async def save_user_karma(callback_query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    await callback_query.answer()
    index = int(callback_data["index"])
    chat_id = int(callback_data["chat_id"])
    elem = get_element_approve(index)
    user_tg = types.User(**json.loads(elem['founded_user']))

    user = await User.get_or_create_from_tg_user(user_tg)
    await save_karma(user, chat_id, elem['karma'])
    await callback_query.message.edit_text(**next_approve(get_element_approve(index+1), index+1, chat_id))


def save_problems_list(problem: type_karmas):
    with PROBLEMS_FILE.open("r") as f:
        problems = json.load(f)
    problems.append(problem)
    with PROBLEMS_FILE.open("w") as f:
        json.dump(problems, f)


def get_problems_list() -> str:
    with PROBLEMS_FILE.open("r") as f:
        problems = json.load(f)
    return get_text_problems_users(problems)


def get_text_problems_users(problems: typing.List[type_karmas]) -> str:
    problems_users = "Список пользователей с проблемами:"
    for name, username, karma in problems:
        problems_users += f"\n{quote_html(name)} @{quote_html(username)} {hbold(karma)}"
    return problems_users
