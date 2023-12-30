import logging

from aiogram import types

from app.infrastructure.database.repo.chat import ChatRepo
from app.infrastructure.database.repo.chat_settings import ChatSettingsRepo
from app.infrastructure.database.repo.user import UserRepo

logger = logging.getLogger(__name__)


async def setup_chat(
    chat_repo: ChatRepo,
    user_repo: UserRepo,
    chat_settings_repo: ChatSettingsRepo,
    tg_user: types.User,
    tg_chat: types.Chat | None = None,
):
    try:
        chat = None
        chat_settings = None
        user = await user_repo.get_or_create_from_tg_user(tg_user)

        if tg_chat and tg_chat.type != "private":
            chat = await chat_repo.get_or_create_from_tg_chat(tg_chat)
            chat_settings = await chat_settings_repo.get_or_create(chat=chat)

        return user, chat, chat_settings
    except Exception as e:
        logger.exception("troubles with db", exc_info=e)
        raise e
