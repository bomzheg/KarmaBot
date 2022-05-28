from __future__ import annotations
from dataclasses import dataclass

from enum import Enum

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.storage import BaseStorage
from loguru import logger


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

    def create_redis_storage(self) -> RedisStorage2:
        logger.info("created storage for {self}", self=self)
        return RedisStorage2(host=self.url, port=self.port, db=self.db)

