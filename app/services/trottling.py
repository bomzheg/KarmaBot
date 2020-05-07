from aiogram import Dispatcher
from aiogram.utils.executor import Executor

from app import config
from app.utils.redis import BaseRedis


class ThrottlingService(BaseRedis):
    def __init__(self, prefix="throttling", expiration_min: int = 1, *args, **kwargs):
        super(ThrottlingService, self).__init__(*args, **kwargs)
        self.prefix = prefix
        self.expire_sec = expiration_min * 60

    def _create_key_chat(self, chat_id: int, command: str) -> str:
        return f"{self.prefix}:{chat_id}:{command}"

    def _create_key_user(self, chat_id: int, user_id: int, command: str) -> str:
        return f"{self.prefix}:{chat_id}:{user_id}:{command}"

    async def set_chat_command(self, command: str, chat_id: int):
        key = self._create_key_chat(chat_id, command)
        if await self.redis.get(key) is not None:
            return False
        return await self.redis.set(key, command, expire=self.expire_sec, exist=True)

    async def set_user_command(self, command: str, chat_id: int, user_id: int):
        key = self._create_key_user(chat_id, user_id, command)
        if await self.redis.get(key) is not None:
            return False
        return await self.redis.set(key, command, expire=self.expire_sec, exist=True)


throttling = ThrottlingService(
    host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB
)


async def on_startup(dispatcher: Dispatcher):
    await throttling.connect()


async def on_shutdown(dispatcher: Dispatcher):
    await throttling.disconnect()


def setup(runner: Executor):
    runner.on_startup(on_startup)
    runner.on_shutdown(on_shutdown)
