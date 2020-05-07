# partially from https://github.com/aiogram/bot

from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from app.models.chat import Chat
from app.models.user import User


class ACLMiddleware(BaseMiddleware):

    async def setup_chat(self, data: dict, user: types.User, chat: Optional[types.Chat] = None):
        if chat and chat.type != 'private':
            chat_id = chat.id
        else:
            chat_id = None

        try:
            user = await User.get_or_create_from_tg_user(user)
            if chat_id is not None:
                chat = await Chat.get_or_create_from_tg_chat(chat)

        except Exception as e:
            logger.error("troubles with db")
            raise e

        data["user"] = user
        data["chat"] = chat

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_chat(data, message.from_user, message.chat)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.setup_chat(data, query.from_user, query.message.chat if query.message else None)
