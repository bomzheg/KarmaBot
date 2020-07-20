import asyncio
import typing

from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger
from pyrogram import Client
import pyrogram
from pyrogram.errors import RPCError, UsernameNotOccupied, FloodWait

from app import config
from aiogram.types import User
SLEEP_TIME = 100


class UserGetter:
    def __init__(self):
        self._client_api_bot = Client("karma_bot", bot_token=config.TEST_BOT_TOKEN, api_id=config.API_ID,
                                      api_hash=config.API_HASH)
        self._lock_username = asyncio.Lock()
        self._lock_fullname = asyncio.Lock()

    async def get_user(self, username: str = None, fullname: str = None, chat_id: int = None) -> User:
        async def try_by_name() -> typing.Optional[User]:
            try:
                return await self.get_user_by_fullname(chat_id, fullname)
            except (IndexError, RPCError):
                return None

        if username is not None:
            try:
                user_tg = await self.get_user_by_username(username)
            except RPCError:
                user_tg = await try_by_name()
        else:
            user_tg = await try_by_name()
        return user_tg

    async def get_user_by_username(self, username: str) -> User:
        async with self._lock_username:
            try:
                logger.info("get user of username {username}", username=username)
                user = await self._client_api_bot.get_users(username)
                logger.info("found user {user}", user=self.get_user_dict_for_log(user))
            except UsernameNotOccupied:
                logger.info("Username not found {username}", username=username)
                raise
            except FloodWait as e:
                logger.error("Flood Wait {e}", e=e)
                await asyncio.sleep(e.x)
            finally:
                await asyncio.sleep(SLEEP_TIME)

        return self.get_aiogram_user_by_pyrogram(user)

    async def get_user_by_fullname(self, chat_id: int, fullname: str) -> User:
        async with self._lock_fullname:
            try:
                logger.info("get user of name {name}", name=fullname)
                chat_members = await self._client_api_bot.get_chat_members(chat_id=chat_id, query=fullname)
                logger.info(
                    "found: {users}",
                    users=[self.get_user_dict_for_log(chat_member.user) for chat_member in chat_members]
                )
                user = chat_members[0].user
            except IndexError:
                logger.info("name not found {name}", name=fullname)
                raise
            except FloodWait as e:
                logger.error("Flood Wait {e}", e=e)
                await asyncio.sleep(e.x)
            finally:
                await asyncio.sleep(SLEEP_TIME)
        return self.get_aiogram_user_by_pyrogram(user)

    @staticmethod
    def get_aiogram_user_by_pyrogram(user: pyrogram.User) -> User:
        return User(
            id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
        )

    @staticmethod
    def get_user_dict_for_log(user: pyrogram.User) -> dict:
        return dict(
            id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

    async def start(self):
        await self._client_api_bot.start()

    async def stop(self):
        await self._client_api_bot.stop()


user_getter = UserGetter()


async def on_startup(_: Dispatcher):
    await user_getter.start()


async def on_shutdown(_: Dispatcher):
    await user_getter.stop()


def setup(runner: Executor):

    runner.on_startup(on_startup)
    runner.on_shutdown(on_shutdown)


__all__ = [user_getter, RPCError]
