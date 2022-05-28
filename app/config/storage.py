from typing import Any

from app.models.config.storage import StorageConfig, StorageType, RedisConfig


def load_storage(dct: dict[str, Any]) -> StorageConfig:
    config = StorageConfig(type_=StorageType[dct["type"]])
    if config.type_ == StorageType.redis:
        config.redis = RedisConfig(
            url=dct["redis"]["url"],
            port=int(dct["redis"]["port"]),
            db=int(dct["redis"]["db"]),
        )
    return config
