# partially from https://github.com/aiogram/bot

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, types
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types import TelegramObject

from app.infrastructure.database.repo.chat import ChatRepo
from app.infrastructure.database.repo.chat_settings import ChatSettingsRepo
from app.infrastructure.database.repo.report import ReportRepo
from app.infrastructure.database.repo.user import UserRepo
from app.services.setup_chat import setup_chat
from app.utils.log import Logger

logger = Logger(__name__)


class DBMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        chat: types.Chat = data.get("event_chat", None)
        user: types.User = data.get("event_from_user", None)
        if isinstance(event, types.Message) and event.sender_chat:
            raise CancelHandler

        # TODO: need to pass db session here
        chat_repo = ChatRepo()
        user_repo = UserRepo()
        report_repo = ReportRepo()
        chat_settings_repo = ChatSettingsRepo()

        user, chat, chat_settings = await setup_chat(
            tg_user=user,
            tg_chat=chat,
            user_repo=user_repo,
            chat_repo=chat_repo,
            chat_settings_repo=chat_settings_repo,
        )

        data["chat_repo"] = chat_repo
        data["user_repo"] = user_repo
        data["report_repo"] = report_repo
        data["chat_settings_repo"] = chat_settings_repo

        data["user"] = user
        data["chat"] = chat
        data["chat_settings"] = chat_settings

        return await handler(event, data)
