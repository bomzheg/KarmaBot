from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from app.utils.log import Logger

logger = Logger(__name__)


class StorageType(Enum):
    memory = "memory"
    redis = "redis"


@dataclass
class StorageConfig:
    type_: StorageType
    redis: RedisConfig | None = None

    def create_storage(self) -> BaseStorage:
        logger.info("creating storage for type {type}", type=self.type_)
        match self.type_:
            case StorageType.memory:
                return MemoryStorage()
            case StorageType.redis:
                return self.redis.create_redis_storage()
            case _:
                raise NotImplementedError


@dataclass
class RedisConfig:
    url: str
    port: int = 6379
    db: int = 1

    def create_redis_storage(self) -> RedisStorage:
        logger.info("created storage for {self}", self=self)
        return RedisStorage(Redis(host=self.url, port=self.port, db=self.db))
