import asyncio
import typing

from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger
from pyrogram import Client
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

    async def get_user(self, username: str) -> User:
        return (await self.get_users([username]))[0][0]

    async def get_users(
            self,
            usernames: typing.Union[typing.List[str], typing.Set[str]]
    ) -> typing.Tuple[typing.List[User], typing.List[str]]:

        count, time = self.calculate_time(usernames, SLEEP_TIME)
        logger.info("for {count} usernames it take about {time}", count=count, time=time)

        users = []
        errors_username = []
        async with self._lock_username:
            for username in usernames:
                try:
                    user = await self._client_api_bot.get_users(username)
                    users.append(user)
                    logger.info("get user of username {username}", username=username)
                except UsernameNotOccupied:
                    logger.info("Username not found {username}", username=username)
                    errors_username.append(username)
                except FloodWait as e:
                    logger.error("Flood Wait {e}", e=e)
                    await asyncio.sleep(e.x)
                finally:
                    await asyncio.sleep(SLEEP_TIME)
        correct_users = [User(
            id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
        ) for user in users]
        return correct_users, errors_username

    @staticmethod
    def calculate_time(array, sleep_time):
        count = len(array)
        time = count * sleep_time // 60
        if time > 60:
            hours = time // 60
            minutes = time % 60
            time = f"{hours} h {minutes} m"
        else:
            time = f"{time} min"
        return count, time

    async def get_users_by_fullname(
            self,
            chat_id: int,
            fullnames: typing.Union[typing.List[str], typing.Set[str]]
    ) -> typing.List[User]:
        count, time = self.calculate_time(fullnames, SLEEP_TIME)
        logger.info("for {count} fullnames it take about {time}", count=count, time=time)

        users = []
        async with self._lock_fullname:
            for fullname in fullnames:
                try:
                    logger.info("get user of name {name}", name=fullname)
                    user = await self._client_api_bot.get_chat_members(chat_id=chat_id, query=fullname)
                    users.append(user[0].user)
                except IndexError:
                    logger.info("name not found {name}", name=fullname)
                except FloodWait as e:
                    logger.error("Flood Wait {e}", e=e)
                    await asyncio.sleep(e.x)
                finally:
                    await asyncio.sleep(SLEEP_TIME)
        correct_users = [User(
            id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
        ) for user in users]
        return correct_users

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
