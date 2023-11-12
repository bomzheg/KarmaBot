from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject

from app.models.config import Config
from app.utils.log import Logger

logger = Logger(__name__)


class ConfigMiddleware(BaseMiddleware):
    def __init__(self, config: Config):
        super(ConfigMiddleware, self).__init__()
        self.config = config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["config"]: Config = self.config
        return await handler(event, data)
