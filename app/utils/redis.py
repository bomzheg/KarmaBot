# from https://github.com/aiogram/bot
from typing import Optional

import aioredis
from loguru import logger


class BaseRedis:
    def __init__(self, host: str, port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db

        self._redis: Optional[aioredis.Redis] = None

    @property
    def closed(self):
        return not self._redis or self._redis.closed

    async def connect(self):
        if self.closed:
            self._redis = await aioredis.create_redis_pool((self.host, self.port), db=self.db)

    async def disconnect(self):
        if not self.closed:
            self._redis.close()
            await self._redis.wait_closed()

    @property
    def redis(self) -> aioredis.Redis:
        if self.closed:
            raise RuntimeError("Redis connection is not opened")
        return self._redis

    async def remove_all_fsm(self):
        keys = await self.redis.keys(f'fsm:*')
        if len(keys) == 0:
            return logger.warning("fsm-keys to delete not found")
        logger.warning("Next keys was deleted " + ", ".join(keys))
        await self.redis.delete(*keys)
