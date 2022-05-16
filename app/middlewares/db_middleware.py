# partially from https://github.com/aiogram/bot

from typing import Optional

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from app.models.config import TgClientConfig
from app.models.db import Chat, User
from app.services.find_target_user import get_db_user_by_tg_user
from app.services.settings import get_chat_settings
from app.utils.lock_factory import LockFactory
from app.utils.log import Logger


logger = Logger(__name__)


class DBMiddleware(BaseMiddleware):
    def __init__(self, tg_client_config: TgClientConfig):
        super(DBMiddleware, self).__init__()
        self.lock_factory = LockFactory()
        self.tg_client_config = tg_client_config

    async def setup_chat(self, data: dict, user: types.User, chat: Optional[types.Chat] = None):
        try:
            async with self.lock_factory.get_lock(f"{user.id}"):
                user = await User.get_or_create_from_tg_user(user)
            if chat and chat.type != 'private':
                async with self.lock_factory.get_lock(f"{chat.id}"):
                    chat = await Chat.get_or_create_from_tg_chat(chat)
                    data["chat_settings"] = await get_chat_settings(chat=chat)

        except Exception as e:
            logger.exception("troubles with db", exc_info=e)
            raise e
        data["user"] = user
        data["chat"] = chat

    async def fix_target(self, data: dict):
        try:
            target: types.User = data['target']
        except KeyError:
            return
        target = await get_db_user_by_tg_user(target, self.tg_client_config)
        data['target'] = target

    async def on_pre_process_message(self, message: types.Message, data: dict):
        if message.sender_chat:
            raise CancelHandler
        await self.setup_chat(data, message.from_user, message.chat)

    async def on_process_message(self, _: types.Message, data: dict):
        await self.fix_target(data)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.setup_chat(data, query.from_user, query.message.chat if query.message else None)
