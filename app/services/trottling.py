from app.utils.redis import BaseRedis
from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger
from app import config



class TrottlingService(BaseRedis):
    def __init__(self, prefix="trottling", expiration_min: int = 1, *args, **kwargs):
        super(TrottlingService, self).__init__(*args, **kwargs)
        self.prefix = prefix
        self.expire_sec = expiration_min * 60

    def _create_key(self, chat_id: int, command: str) -> str:
        return f"{self.prefix}:{chat_id}:{command}"
    
    async def set_command(self, command: str, chat_id: int):
        key = self._create_key(chat_id, command)
        if await self.redis.get(key) is not None:
            return False
        return await self.redis.set(key, command, expire=self.expire_sec, exist=True)



trottling = TrottlingService(
    host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB
)


async def on_startup(dispatcher: Dispatcher):
    await trottling.connect()


async def on_shutdown(dispatcher: Dispatcher):
    await trottling.disconnect()


def setup(runner: Executor):
    runner.on_startup(on_startup)
    runner.on_shutdown(on_shutdown)