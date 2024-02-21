import asyncio

import pyrogram
from aiogram.types import User
from pyrogram import Client
from pyrogram.errors import FloodWait, UsernameNotOccupied

from app.models.config import TgClientConfig
from app.services.restrict_call import RestrictCall
from app.utils.log import Logger

logger = Logger(__name__)


class UserGetter:
    def __init__(self, client_config: TgClientConfig):
        self._client_api_bot = Client(
            "karma_bot",
            bot_token=client_config.bot_token,
            api_id=client_config.api_id,
            api_hash=client_config.api_hash,
            no_updates=True,
        )
        self.restrict = RestrictCall(client_config.request_interval)
        self.restrict_methods = ("get_users",)
        self.patch_api_client()

    def patch_api_client(self):
        for method in self.restrict_methods:
            patched = self.restrict(getattr(self._client_api_bot, method))
            setattr(self._client_api_bot, method, patched)

    async def get_user_by_username(self, username: str) -> User:
        try:
            logger.info("get user of username {username}", username=username)
            user = await self._client_api_bot.get_users(username)
            logger.info("found user {user}", user=self.get_user_dict_for_log(user))
        except UsernameNotOccupied:
            logger.info("Username not found {username}", username=username)
            raise
        except FloodWait as e:
            logger.error("Flood Wait {e}", e=e)
            await asyncio.sleep(e.value)
            raise Exception("Username resolver encountered flood error. Waited for %s", e.value)

        return self.get_aiogram_user_by_pyrogram(user)

    @staticmethod
    def get_aiogram_user_by_pyrogram(user: pyrogram.types.User) -> User:
        return User(
            id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
        )

    @staticmethod
    def get_user_dict_for_log(user: pyrogram.types.User) -> dict:
        return dict(
            id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

    async def start(self):
        self.restrict.start_worker()
        if not self._client_api_bot.is_connected:
            await self._client_api_bot.start()

    async def stop(self):
        self.restrict.stop_worker()
        if self._client_api_bot.is_connected:
            await self._client_api_bot.stop()

    async def __aenter__(self) -> "UserGetter":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
