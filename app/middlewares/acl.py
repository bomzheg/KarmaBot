# partially from https://github.com/aiogram/bot

from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from app.models import Chat, User
from app.services.find_target_user import get_db_user_by_tg_user
from app.utils.lock_factory import LockFactory


class ACLMiddleware(BaseMiddleware):
    def __init__(self):
        super(ACLMiddleware, self).__init__()
        self.lock_factory = LockFactory()

    async def setup_chat(self, data: dict, user: types.User, chat: Optional[types.Chat] = None):
        try:
            async with self.lock_factory.get_lock(f"{user.id}"):
                user = await User.get_or_create_from_tg_user(user)
            if chat and chat.type != 'private':
                async with self.lock_factory.get_lock(f"{chat.id}"):
                    chat = await Chat.get_or_create_from_tg_chat(chat)

        except Exception as e:
            logger.error("troubles with db")
            raise e
        data["user"] = user
        data["chat"] = chat

    @staticmethod
    async def fix_target(data: dict):
        try:
            target: types.User = data['target']
        except KeyError:
            return
        target = await get_db_user_by_tg_user(target)
        data['target'] = target

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_chat(data, message.from_user, message.chat)

    async def on_process_message(self, _: types.Message, data: dict):
        await self.fix_target(data)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.setup_chat(data, query.from_user, query.message.chat if query.message else None)
