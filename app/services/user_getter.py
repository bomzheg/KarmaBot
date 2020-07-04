import typing

from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from pyrogram import Client
from pyrogram.errors import RPCError
from app import config
from aiogram.types import User
MAX_USERNAMES = 200

_client_api_bot: Client


async def get_user(username: str) -> User:
    return (await get_users([username]))[0]


async def get_users(usernames: typing.Iterable[str]) -> typing.List[User]:
    if len(usernames) >= MAX_USERNAMES:
        precursor = [await get_users(usernames_chunk) for usernames_chunk in group(usernames, MAX_USERNAMES - 1)]
        return list(*precursor)
    users = await _client_api_bot.get_users(usernames)

    return [User(
        id=user.id,
        is_bot=user.is_bot,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.language_code,
    ) for user in users]


def group(iterable, count):
    """ group elements list by count elements """

    return zip(*[iter(iterable)] * count)


async def on_startup(_: Dispatcher):
    global _client_api_bot
    _client_api_bot = Client("karma_bot", bot_token=config.now_token, api_id=config.API_ID,
                             api_hash=config.API_HASH)
    await _client_api_bot.start()


async def on_shutdown(_: Dispatcher):
    await _client_api_bot.stop()


def setup(runner: Executor):

    runner.on_startup(on_startup)
    runner.on_shutdown(on_shutdown)


__all__ = [get_user, get_users, RPCError]
