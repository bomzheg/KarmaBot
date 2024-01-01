import asyncio

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.utils.text_decorations import html_decoration as hd
from tortoise.exceptions import DoesNotExist

from app.infrastructure.database.models import Chat, User
from app.infrastructure.database.repo.chat import ChatRepo
from app.infrastructure.database.repo.user import UserRepo
from app.models.config import Config
from app.services.karma import get_me_chat_info, get_me_info
from app.services.karma import get_top as get_karma_top
from app.services.remove_message import cleanup_command_dialog
from app.utils.log import Logger

logger = Logger(__name__)
router = Router(name=__name__)


@router.message(Command("top", prefix="!"), F.chat.type == "private")
async def get_top_from_private(
    message: types.Message,
    user: User,
    chat_repo: ChatRepo,
    user_repo: UserRepo,
    config: Config,
    bot: Bot,
):
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        bot_reply = await message.reply(
            "Эту команду можно использовать только в группах "
            "или с указанием ID нужного чата, например:"
            "\n" + hd.code("!top -1001399056118")
        )
        return asyncio.create_task(
            cleanup_command_dialog(
                bot=bot,
                bot_message=bot_reply,
                delete_bot_reply=True,
                delay=config.time_to_remove_temp_messages,
            )
        )
    try:
        chat = await chat_repo.get_by_id(chat_id=int(parts[1]))
    except DoesNotExist:
        bot_reply = await message.reply(
            "Не удалось найти чат с таким ID, убедитесь, "
            "что бот состоит в этом чате и попробуйте еще раз"
        )
        return asyncio.create_task(
            cleanup_command_dialog(
                bot=bot,
                bot_message=bot_reply,
                delete_bot_reply=True,
                delay=config.time_to_remove_temp_messages,
            )
        )
    logger.info(
        "user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id
    )
    text = await get_karma_top(chat, user, chat_repo=chat_repo, user_repo=user_repo)

    await message.reply(text, disable_web_page_preview=True)


@router.message(Command("top", prefix="!"))
async def get_top(
    message: types.Message,
    chat: Chat,
    user: User,
    chat_repo: ChatRepo,
    user_repo: UserRepo,
    config: Config,
    bot: Bot,
):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        bot_reply = await message.reply(
            "Просмотр топа другого чата возможен только в личных сообщениях с ботом"
        )
        return asyncio.create_task(
            cleanup_command_dialog(
                bot=bot,
                bot_message=bot_reply,
                delete_bot_reply=True,
                delay=config.time_to_remove_temp_messages,
            )
        )

    logger.info(
        "user {user} ask top karma of chat {chat}", user=user.tg_id, chat=chat.chat_id
    )
    text = await get_karma_top(chat, user, chat_repo=chat_repo, user_repo=user_repo)

    await message.reply(text, disable_web_page_preview=True)


@router.message(F.chat.type.in_(["group", "supergroup"]), Command("me", prefix="!"))
async def get_me(
    message: types.Message, chat: Chat, user: User, config: Config, bot: Bot
):
    logger.info(
        "user {user} ask his karma in chat {chat}", user=user.tg_id, chat=chat.chat_id
    )
    uk, number_in_top = await get_me_chat_info(chat=chat, user=user)
    bot_reply = await message.reply(
        f"Ваша карма в данном чате: <b>{uk.karma:.2f}</b> ({number_in_top})",
        disable_web_page_preview=True,
    )

    return asyncio.create_task(
        cleanup_command_dialog(
            bot=bot,
            bot_message=bot_reply,
            delete_bot_reply=True,
            delay=config.time_to_remove_temp_messages,
        )
    )


@router.message(F.chat.type == "private", Command("me", prefix="!"))
async def get_me_private(message: types.Message, user: User):
    logger.info("user {user} ask his karma", user=user.tg_id)
    uks = await get_me_info(user)
    text = ""
    for uk, number_in_top in uks:
        text += f"\n{uk.chat.mention} <b>{uk.karma:.2f}</b> ({number_in_top})"
    if text:
        return await message.reply(
            f"У Вас есть карма в следующих чатах:{text}", disable_web_page_preview=True
        )
    await message.reply(
        "У Вас нет никакой кармы ни в каких чатах", disable_web_page_preview=True
    )
