# partially from https://github.com/aiogram/bot

from typing import Optional, Callable, Dict, Any, Awaitable

from aiogram import types, BaseMiddleware
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types import TelegramObject
from tortoise.transactions import in_transaction

from app.infrastructure.database.models import User
from app.infrastructure.database.repo.chat import ChatRepo
from app.services.settings import get_chat_settings
from app.utils.lock_factory import LockFactory
from app.utils.log import Logger


logger = Logger(__name__)


class DBMiddleware(BaseMiddleware):
    def __init__(self, lock_factory: LockFactory):
        super(DBMiddleware, self).__init__()
        self.lock_factory = lock_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        chat: types.Chat = data.get("event_chat", None)
        user: types.User = data.get("event_from_user", None)
        if isinstance(event, types.Message) and event.sender_chat:
            raise CancelHandler
        await self.setup_chat(data, user, chat)
        return await handler(event, data)

    async def setup_chat(self, data: dict, user: types.User, chat: Optional[types.Chat] = None):
        try:
            async with in_transaction() as db_session:
                chat_repo = ChatRepo(db_session)

                async with self.lock_factory.get_lock(user.id):
                    user = await User.get_or_create_from_tg_user(user)
                if chat and chat.type != 'private':
                    async with self.lock_factory.get_lock(chat.id):
                        chat = await chat_repo.get_or_create_from_tg_chat(chat)
                        data["chat_settings"] = await get_chat_settings(chat=chat)

        except Exception as e:
            logger.exception("troubles with db", exc_info=e)
            raise e

        data["chat_repo"] = chat_repo
        data["user"] = user
        data["chat"] = chat
